import os
import tempfile
import time
from functools import cached_property

import requests
from bs4 import BeautifulSoup
from utils import File, Hash, Log

log = Log("WebPage")


class WebPage(object):
    def __init__(self, url, do_cache=False):
        self.url = url
        self.do_cache = do_cache

    @staticmethod
    def get_temp_data_path():
        return os.path.join(tempfile.gettempdir(), "scraper_genelecsl2024")

    TEMP_DATA_PATH = get_temp_data_path()

    @cached_property
    def params(self) -> dict[str, str]:
        return dict(
            [param.split("=") for param in self.url.split("?")[1].split("&")]
        )

    @staticmethod
    def get_html_dir(TEMP_DATA_PATH):
        html_dir = os.path.join(TEMP_DATA_PATH, "common", "html")
        if not os.path.exists(html_dir):
            os.makedirs(html_dir)
        return html_dir

    HTML_DIR = get_html_dir(TEMP_DATA_PATH)

    @cached_property
    def html(self):
        html_path = os.path.join(WebPage.HTML_DIR, Hash.md5(self.url) + ".html")
        html_file = File(html_path)
        if html_file.exists and self.do_cache:
            log.debug(f"File exists: {html_path}")
            return html_file.read()

        timeout = 10
        html = None
        while True:
            log.debug(f"🌏 {self.url} [{timeout}s]")
            try:
                html = requests.get(self.url, timeout=timeout).text
                break
            except Exception as e:
                log.error(f"Error: {e}")
                timeout = int(timeout * 1.5)
                time.sleep(timeout)

        n = len(html)
        size_k = n / 1024
        html_file.write(html)
        log.debug(f"Wrote {html_path} {size_k:.2f}KB")
        return html

    @cached_property
    def soup(self):
        return BeautifulSoup(self.html, "html.parser")
