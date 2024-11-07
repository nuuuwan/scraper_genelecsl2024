import os
from functools import cached_property

from utils import Log

from core import OngoingElection
from utils_future import TSVFile, WebPage

log = Log("AbstractScraper")


class AbstractScraper(object):

    @classmethod
    def get_id(cls):
        return cls.__name__.lower()

    @cached_property
    def election_nocache(self) -> OngoingElection:
        log.info(f"Found {len(self.pd_results)} PD Results")
        return OngoingElection(self.pd_results)

    @cached_property
    def election(self) -> OngoingElection:
        election_path = os.path.join(
            WebPage.TEMP_DATA_PATH,
            self.__class__.get_id(),
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
