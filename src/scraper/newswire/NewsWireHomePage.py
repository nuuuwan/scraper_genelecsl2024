from functools import cached_property

from gig import Ent, EntType
from utils import Log

from utils_future import WebPage

log = Log("NewsWireHomePage")


class NewsWireHomePage(WebPage):
    def __init__(self):
        super().__init__("https://election.newswire.lk/")

    @cached_property
    def ed_id_to_href(self):
        soup = self.soup
        div_list = soup.find_all("div", {"class": "card card-widget wbconts"})
        ed_id_to_href = {}
        for div in div_list:
            h2 = div.find("h2")
            ed_name = " ".join(h2.text.split("  ")[:-1])
            ent = Ent.list_from_name_fuzzy(ed_name, EntType.ED, limit=1)[0]
            ed_id = ent.id

            a = div.find("a")
            href = a["href"]

            ed_id_to_href[ed_id] = href
        log.info(f"Found hrefs for {len(ed_id_to_href)} EDs")
        return ed_id_to_href
