from functools import cached_property

from elections_lk import Result
from utils import Log

from scraper.AbstractScraper import AbstractScraper
from scraper.eclk.ECLKHomePage import ECLKHomePage

log = Log("ECLK")


class ECLK(AbstractScraper):

    @cached_property
    def pd_results(self) -> list[Result]:
        pd_results = []
        for results_page in ECLKHomePage().results_page_list:
            results_page.pd_result
            pd_results.append(results_page.pd_result)

        return pd_results
