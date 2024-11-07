import os
from functools import cached_property

from elections_lk import PartyToVotes, Result, VoteSummary
from gig import Ent, EntType
from utils import JSONFile, Log

from scraper.AbstractScraper import AbstractScraper
from utils_future import StringX, WebPage

log = Log("ECLKResultsPage")


class ECLKResultsPage(WebPage):
    def __init__(self, href):
        super().__init__("https://results.elections.gov.lk/pre2024/" + href)

    ED_NAME_IDX = {"Mahanuwara": "Kandy"}
    PD_NAME_IDX = {"Nuwara Eliya Maskeliya": "N.E.Maskeliya"}

    @cached_property
    def pd_id(self) -> str:
        pd_division = self.params["pd_division"]
        district = self.params["district"]

        if "Postal" in pd_division:
            ed_name = self.ED_NAME_IDX.get(district, district)

            ed = Ent.list_from_name_fuzzy(ed_name, EntType.ED)[0]
            return ed.id + "P"

        pd_name = self.PD_NAME_IDX.get(pd_division, pd_division)
        pd = Ent.list_from_name_fuzzy(pd_name, EntType.PD)[0]
        return pd.id

    @staticmethod
    def parse_party_to_votes(table) -> PartyToVotes:
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

    SUMMARY_KEY_IDX = {
        "Total Electors": "electors",
        "Total Polled": "polled",
        "Rejected Votes": "rejected",
        "Valid Votes": "valid",
    }

    @staticmethod
    def parse_vote_summary(table) -> VoteSummary:
        tr_list = table.find_all("tr")
        d = {}
        for tr in tr_list:
            td_text_list = [td.text.strip() for td in tr.find_all("td")]
            if len(td_text_list) != 3:
                continue

            key = td_text_list[0]
            key = ECLKResultsPage.SUMMARY_KEY_IDX[key]
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
    def get_pd_result_dir() -> str:
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
    def pd_result_nocache(self) -> Result:

        table_list = self.soup.find_all("table")

        result = Result(
            id=self.pd_id,
            vote_summary=self.parse_vote_summary(table_list[1]),
            party_to_votes=self.parse_party_to_votes(table_list[0]),
        )
        self.validate(result)

        return result

    @cached_property
    def pd_result(self) -> Result:

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
