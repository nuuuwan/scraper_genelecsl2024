import os
import tempfile


class AbstractScraper(object):

    @staticmethod
    def get_temp_data_path():
        return os.path.join(tempfile.gettempdir(), "scraper_genelecsl2024")

    TEMP_DATA_PATH = get_temp_data_path()
