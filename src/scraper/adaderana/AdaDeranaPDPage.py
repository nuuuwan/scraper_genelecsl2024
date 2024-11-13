from functools import cache, cached_property

from elections_lk import PartyToVotes, Result, VoteSummary
from gig import Ent, EntType

from scraper.AbstractPDResultsPage import AbstractPDResultsPage
from utils_future import StringX


class AdaDeranaPDPage(AbstractPDResultsPage):
    def __init__(self, ed_label, pd_label):
        super().__init__(
            "https://election.adaderana.lk"
            + "/presidential-election-2024/division_result.php?"
            + f"dist_id={ed_label}&div_id={pd_label}",
            do_cache=True,
        )
        self.ed_label = ed_label
        self.pd_label = pd_label

    @classmethod
    @cache
    def get_id(cls) -> str:
        return "adaderana"

    ED_NAME_IDX = {
        "Mahanuwara": "Kandy",
    }
    PD_NAME_IDX = {
        "NEliya-Maskeliya": "Nuwara Eliya Maskeliya",
    }

    @cached_property
    def pd_id(self) -> str:
        pd_label = self.pd_label
        ed_label = self.ed_label

        if "Postal" in pd_label:
            ed_name = self.ED_NAME_IDX.get(ed_label, ed_label)

            ed = Ent.list_from_name_fuzzy(ed_name, EntType.ED)[0]
            return ed.id + "P"

        pd_name = self.PD_NAME_IDX.get(pd_label, pd_label)
        pd = Ent.list_from_name_fuzzy(pd_name, EntType.PD)[0]
        return pd.id

    @cached_property
    def party_to_votes(self) -> PartyToVotes:
        div = self.soup.find("div", class_="district")
        party_to_votes = {}
        for div_row in div.find_all("div", class_="dis_ele_result"):
            div_party = div_row.find("div", class_="ele_party")
            span_party = div_party.find("span")
            party = span_party.text.strip()
            div_votes = div_row.find("div", class_="ele_value")
            span_votes = div_votes.find("span")
            votes = StringX(span_votes.text.strip()).int
            party_to_votes[party] = votes
        return PartyToVotes(party_to_votes)

    @cached_property
    def vote_summary(self) -> VoteSummary:
        table = self.soup.find("table")
        idx = {}
        for tr in table.find_all("tr"):
            k = tr.find("th").text.strip()
            v = tr.find("td").text.strip()
            k = k.lower()
            v = StringX(v).int
            idx[k] = v
        return VoteSummary(
            idx["electors"],
            idx["polled"],
            idx["valid"],
            idx["rejected"],
        )

    @cached_property
    def pd_result_nocache(self):
        return Result(self.pd_id, self.vote_summary, self.party_to_votes)
