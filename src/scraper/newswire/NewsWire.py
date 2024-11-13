from functools import cached_property

from elections_lk import Result
from utils import Log

from scraper.AbstractScraper import AbstractScraper
from scraper.newswire.NewsWireEDPage import NewsWireEDPage
from scraper.newswire.NewsWireHomePage import NewsWireHomePage

log = Log("NewsWire")


class NewsWire(AbstractScraper):

    @cached_property
    def pd_results(self) -> list[Result]:
        pd_results = []
        ed_id_to_href = NewsWireHomePage().ed_id_to_href
        for ed_id, href in ed_id_to_href.items():
            ed_page = NewsWireEDPage(ed_id, href)
            pd_results_for_ed = ed_page.pd_results
            pd_results.extend(pd_results_for_ed)

        return pd_results
