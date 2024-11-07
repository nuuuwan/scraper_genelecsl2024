from functools import cached_property

from scraper.adaderana.AdaDeranaEDPage import AdaDeranaEDPage
from src.scraper.AbstractScraper import AbstractScraper


class AdaDerana(AbstractScraper):
    @cached_property
    def pd_results(self):
        pd_results = []
        for ed_page in AdaDeranaEDPage.list_all():
            for pd_page in ed_page.pd_page_list:
                pd_results.append(pd_page.pd_result)
        return pd_results
