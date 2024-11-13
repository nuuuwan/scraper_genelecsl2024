import os
from functools import cache, cached_property

from utils import Log

from core import OngoingElection
from utils_future import TSVFile, WebPage

log = Log("AbstractScraper")


class AbstractScraper(object):

    @classmethod
    @cache
    def get_id(cls):
        return cls.__name__.lower()

    @classmethod
    @cache
    def get_temp_dir(cls):
        temp_dir = os.path.join(
            WebPage.TEMP_DATA_PATH,
            cls.get_id(),
        )
        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir)
        return temp_dir

    @cached_property
    def election_nocache(self) -> OngoingElection:
        log.info(f"Found {len(self.pd_results)} PD Results")
        return OngoingElection(self.pd_results)

    @cached_property
    def election(self) -> OngoingElection:
        election_path = os.path.join(
            self.get_temp_dir(),
            "election.tsv",
        )
        election_file = TSVFile(election_path)
        if election_file.exists:
            log.warning(f"File Exists {election_path}")

        election = self.election_nocache
        election_file.write(election.d_list)

        log.info(f"Wrote {election_path}")
        return election
