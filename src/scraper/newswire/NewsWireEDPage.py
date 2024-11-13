from functools import cached_property

from elections_lk import PartyToVotes, Result, VoteSummary
from utils import Log

from utils_future import StringX, WebPage

log = Log("NewsWireEDPage")


class NewsWireEDPage(WebPage):
    CANDIDATE_TO_PARTY = {
        "ANURA KUMARA DISSANAYAKE": f"NPP",
        "RANIL WICKREMESINGHE": f"IND16",
        "SAJITH PREMADASA": f"SJB",
        "NAMAL RAJAPAKSA": f"SLPP",
        "DILITH JAYAWEERA": f"SLCP",
        "ARIYANETHIRAN PAKKIYASELVAM": f"IND9",
    }

    def __init__(self, ed_id, href):
        super().__init__(href)

        self.ed_id = ed_id
        self.href = href

    def get_vote_summary(self, div):
        table = div.find_all("table")[1]

        d = {}
        for tr in table.find_all("tr"):
            td_list = tr.find_all("td")

            key = {
                "Total Registered votes": "electors",
                "Total Polled": "polled",
                "Rejected Votes": "rejected",
                "Valid Votes": "valid",
            }[td_list[0].text.strip()]
            value = StringX(td_list[1].text.strip()).int
            d[key] = value

        return VoteSummary(
            d["electors"],
            d["polled"],
            d["valid"],
            d["rejected"],
        )

    def get_party_to_votes(self, div):
        table = div.find_all("table")[0]

        d = {}
        for i, tr in enumerate(table.find_all("tr")):
            td_list = tr.find_all("td")
            if len(td_list) < 2:
                continue
            candidate = td_list[0].text.strip()

            party = NewsWireEDPage.CANDIDATE_TO_PARTY.get(candidate, candidate)
            votes = StringX(td_list[1].text.strip()).int
            d[party] = votes

        return PartyToVotes(d)

    def get_pd_result(self, div):
        id = div["id"]
        pd_id = "EC-" + id.split("_")[-1]

        if pd_id.endswith("Z"):
            return None

        assert self.ed_id in pd_id

        return Result(
            id=pd_id,
            vote_summary=self.get_vote_summary(div),
            party_to_votes=self.get_party_to_votes(div),
        )

    @cached_property
    def pd_results(self):
        soup = self.soup
        div_list = soup.find_all("div", class_="accordion")

        pd_results = []
        for div in div_list:
            pd_result = self.get_pd_result(div)
            if pd_result:
                pd_results.append(pd_result)

        log.debug(f"Found {len(pd_results)} pd_results for {self.ed_id}")
        return pd_results
