import os
import tempfile
from functools import cached_property

from utils import Log, TSVFile

from core import OngoingElection

log = Log("AbstractScraper")


class AbstractScraper(object):

    @staticmethod
    def get_temp_data_path():
        return os.path.join(tempfile.gettempdir(), "scraper_genelecsl2024")

    TEMP_DATA_PATH = get_temp_data_path()

    @classmethod
    def id(cls):
        return cls.__name__.lower()

    @cached_property
    def election_nocache(self) -> OngoingElection:
        return OngoingElection(self.pd_results)

    @cached_property
    def election(self) -> OngoingElection:
        election_path = os.path.join(
            AbstractScraper.TEMP_DATA_PATH,
            self.__class__.id(),
            "election.tsv",
        )
        election_file = TSVFile(election_path)
        if election_file.exists:
            d_list = election_file.read()
            log.warning(f"File Exists {election_path}")
            return OngoingElection.from_d_list(d_list)

        election = self.election_nocache
        election_file.write(election.d_list)
        log.info(f"Wrote {election_path}")
        return election
