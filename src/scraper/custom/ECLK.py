import os
import time
from functools import cached_property

import requests
from bs4 import BeautifulSoup
from elections_lk import PartyToVotes, Result, VoteSummary
from gig import Ent, EntType
from utils import File, Hash, JSONFile, Log, TSVFile

from core import OngoingElection
from scraper.AbstractScraper import AbstractScraper
from utils_future import StringX

log = Log("ECLK")


class WebPage(object):
    def __init__(self, url):
        self.url = url

    @staticmethod
    def get_html_dir():
        html_dir = os.path.join(
            AbstractScraper.TEMP_DATA_PATH, "common", "html"
        )
        if not os.path.exists(html_dir):
            os.makedirs(html_dir)
        return html_dir

    HTML_DIR = get_html_dir()

    @cached_property
    def html(self):
        html_path = os.path.join(WebPage.HTML_DIR, Hash.md5(self.url) + ".html")
        html_file = File(html_path)
        if html_file.exists:
            log.warning(f"File Exists {html_path}")
            return html_file.read()

        timeout = 1
        html = None
        while True:
            log.debug(f"[{timeout}s] Opening {self.url}...")
            try:
                html = requests.get(self.url, timeout=timeout).text
                break
            except Exception as e:
                log.error(f"Error: {e}")
                timeout *= 2
                time.sleep(timeout)

        n = len(html)
        size_k = n / 1024
        html_file.write(html)
        log.info(f"Wrote {html_path} {size_k:.2f}KB")
        return html

    @cached_property
    def soup(self):
        return BeautifulSoup(self.html, "html.parser")


class ECLKResultsPage(WebPage):
    def __init__(self, href):
        super().__init__("https://results.elections.gov.lk/pre2024/" + href)

    @cached_property
    def pd_id(self):
        # district=Gampaha&pd_division=Wattala
        tokens = self.url.split("&")
        pd_division = tokens[1].split("=")[-1]
        district = tokens[0].split("=")[-1]

        if "Postal" in pd_division:
            ed_name = {"Mahanuwara": "Kandy"}.get(district, district)

            ed = Ent.list_from_name_fuzzy(ed_name, EntType.ED)[0]
            return ed.id + "P"

        pd_name = {"N.E.Maskeliya": "Nuwara Eliya Maskeliya"}.get(
            pd_division, pd_division
        )
        pd = Ent.list_from_name_fuzzy(pd_name, EntType.PD)[0]
        return pd.id

    @staticmethod
    def parse_party_to_votes(table):
        tr_list = table.find_all("tr")
        d = {}
        for tr in tr_list:

            td_text_list = [td.text.strip() for td in tr.find_all("td")]
            if len(td_text_list) != 4:
                continue

            party = td_text_list[1]
            votes = StringX(td_text_list[2]).int
            d[party] = votes
        d = dict(sorted(d.items(), key=lambda x: x[1], reverse=True))
        return PartyToVotes(d)

    @staticmethod
    def parse_vote_summary(table):
        tr_list = table.find_all("tr")
        d = {}
        for tr in tr_list:
            td_text_list = [td.text.strip() for td in tr.find_all("td")]
            if len(td_text_list) != 3:
                continue

            key = td_text_list[0]
            key = {
                "Total Electors": "electors",
                "Total Polled": "polled",
                "Rejected Votes": "rejected",
                "Valid Votes": "valid",
            }[key]
            value = StringX(td_text_list[1]).int
            d[key] = value

        return VoteSummary(
            d["electors"],
            d["polled"],
            d["valid"],
            d["rejected"],
        )

    @staticmethod
    def validate(result):
        assert result.party_to_votes.total == result.vote_summary.valid
        assert result.vote_summary.electors >= result.vote_summary.polled
        assert (
            result.vote_summary.polled
            == result.vote_summary.valid + result.vote_summary.rejected
        )

    @staticmethod
    def get_pd_result_dir():
        pd_result_dir = os.path.join(
            AbstractScraper.TEMP_DATA_PATH,
            "eclk",
            "pd_results",
        )
        if not os.path.exists(pd_result_dir):
            os.makedirs(pd_result_dir)
        return pd_result_dir

    PD_RESULT_DIR = get_pd_result_dir()

    @cached_property
    def pd_result_nocache(self):

        table_list = self.soup.find_all("table")

        result = Result(
            id=self.pd_id,
            vote_summary=self.parse_vote_summary(table_list[1]),
            party_to_votes=self.parse_party_to_votes(table_list[0]),
        )
        self.validate(result)

        return result

    @cached_property
    def pd_result(self):

        pd_result_path = os.path.join(
            self.PD_RESULT_DIR,
            self.pd_id + ".json",
        )
        pd_result_file = JSONFile(pd_result_path)
        if pd_result_file.exists:
            d = pd_result_file.read()
            log.warning(f"File Exists {pd_result_path}")
            return Result.from_dict(d)

        result = self.pd_result_nocache

        d = result.to_dict()
        pd_result_file.write(d)
        log.info(f"Wrote {pd_result_path}")

        return result


class ECLKHomePage(WebPage):
    def __init__(self):
        super().__init__("https://results.elections.gov.lk/pre2024/")

    @cached_property
    def results_page_list(self):

        results_page_list = []
        for link in self.soup.find_all("a", class_="nav-link"):
            href = link.get("href")
            if "pd_division" not in href:
                continue
            results_page = ECLKResultsPage(href)
            results_page_list.append(results_page)

        log.info(f"Found {len(results_page_list)} Election Results")

        return results_page_list


class ECLK(AbstractScraper):

    @cached_property
    def election_nocache(self) -> OngoingElection:
        pd_results = []
        for results_page in ECLKHomePage().results_page_list:
            results_page.pd_result
            pd_results.append(results_page.pd_result)
        log.info(f"Found {len(pd_results)} PD Results")
        return OngoingElection(pd_results)

    @cached_property
    def election(self) -> OngoingElection:
        election_path = os.path.join(
            AbstractScraper.TEMP_DATA_PATH,
            "eclk",
            "election.tsv",
        )
        election_file = TSVFile(election_path)
        if election_file.exists:
            d_list = election_file.read()
            log.warning(f"File Exists {election_path}")
            return OngoingElection.from_d_list(d_list)

        election = self.election_nocache
        election_file.write(election.d_list)
        log.info(f"Wrote {election_path}")
        return election
