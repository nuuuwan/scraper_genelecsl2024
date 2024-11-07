from functools import cached_property

from gig import Ent, EntType

from scraper.adaderana.AdaDeranaPDPage import AdaDeranaPDPage
from utils_future import WebPage


class AdaDeranaEDPage(WebPage):
    def __init__(self, ed_label):
        super().__init__(
            "https://election.adaderana.lk"
            + "/presidential-election-2024/district_result.php?"
            + f"dist_id={ed_label}"
        )
        self.ed_label = ed_label

    @cached_property
    def pd_page_list(self):
        ul = self.soup.find_all("ul")[4]
        li_list = ul.find_all("li")
        pd_page_list = []
        for li in li_list:
            a = li.find("a")
            pd_label = a.text.strip()
            pd_page = AdaDeranaPDPage(self.ed_label, pd_label)
            pd_page_list.append(pd_page)
        return pd_page_list

    LABEL_TO_NAME = {
        "Kandy": "Mahanuwara",
    }

    @staticmethod
    def list_all() -> list["AdaDeranaEDPage"]:
        webpage_list = []
        for ed in Ent.list_from_type(EntType.ED):
            ed_name = ed.name
            ed_label = AdaDeranaEDPage.LABEL_TO_NAME.get(
                ed_name, ed_name
            ).replace("-", "")
            webpage = AdaDeranaEDPage(ed_label)
            webpage_list.append(webpage)

        return webpage_list
