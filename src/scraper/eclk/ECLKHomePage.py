from functools import cached_property

from utils import Log

from scraper.eclk.ECLKResultsPage import ECLKResultsPage
from utils_future import WebPage

log = Log("ECLKHomePage")


class ECLKHomePage(WebPage):
    def __init__(self):
        # Presidential
        # "https://results.elections.gov.lk/pre2024/"
        super().__init__("https://results.elections.gov.lk/")

    @cached_property
    def results_page_list(self) -> list[ECLKResultsPage]:

        results_page_list = []
        for link in self.soup.find_all("a", class_="nav-link"):
            href = link.get("href")
            if not href:
                continue
            if "pd_division" not in href:
                continue
            results_page = ECLKResultsPage(href)
            results_page_list.append(results_page)

        log.info(f"Found {len(results_page_list)} Election Results")

        return results_page_list
