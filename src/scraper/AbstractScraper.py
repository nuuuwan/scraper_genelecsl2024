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

    @classmethod
    @cache
    def get_election_path(cls):
        return os.path.join(
            cls.get_temp_dir(),
            "election.tsv",
        )

    @cached_property
    def election_nocache(self) -> OngoingElection:
        log.info(f"Found {len(self.pd_results)} PD Results")
        return OngoingElection(self.pd_results)

    @cached_property
    def election(self) -> OngoingElection:
        election_path = self.get_election_path()
        election_file = TSVFile(election_path)

        election = self.election_nocache
        election_file.write(election.d_list)

        log.info(f"Wrote {election_path}")
        return election
