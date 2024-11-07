from functools import cache, cached_property

from elections_lk import PartyToVotes, VoteSummary
from gig import Ent, EntType
from utils import Log

from scraper.AbstractPDResultsPage import AbstractPDResultsPage
from utils_future import StringX

log = Log("ECLKResultsPage")


class ECLKResultsPage(AbstractPDResultsPage):

    def __init__(self, href):
        super().__init__("https://results.elections.gov.lk/pre2024/" + href)

    @classmethod
    @cache
    def get_id(cls):
        return "eclk"

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

    @cached_property
    def party_to_votes(self) -> PartyToVotes:
        table_list = self.soup.find_all("table")
        table = table_list[0]
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

    @cached_property
    def vote_summary(self) -> VoteSummary:
        table_list = self.soup.find_all("table")
        table = table_list[1]
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
