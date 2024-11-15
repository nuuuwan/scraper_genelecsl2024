import os
from functools import cache, cached_property

from elections_lk import Result
from utils import JSONFile, Log, Time, TimeFormat

from core import OngoingResult
from utils_future import WebPage

log = Log("AbstractPDResultsPage")


class AbstractPDResultsPage(WebPage):

    @classmethod
    @cache
    def get_pd_result_dir(cls) -> str:
        pd_result_dir = os.path.join(
            WebPage.TEMP_DATA_PATH,
            cls.get_id(),
            "pd_results",
        )
        if not os.path.exists(pd_result_dir):
            os.makedirs(pd_result_dir)
        return pd_result_dir

    @staticmethod
    def validate(result):

        try:
            assert result.party_to_votes.total <= result.vote_summary.valid
            assert result.vote_summary.electors >= result.vote_summary.polled
            assert (
                result.vote_summary.polled
                == result.vote_summary.valid + result.vote_summary.rejected
            )
        except AssertionError as e:
            log.error(result)
            log.error(f"total={result.party_to_votes.total}")
            raise e

    @cached_property
    def pd_result_nocache(self) -> Result:
        if self.pd_id is None:
            return None
        result = OngoingResult(
            id=self.pd_id,
            vote_summary=self.vote_summary,
            party_to_votes=self.party_to_votes,
            timestamp=self.timestamp,
        )
        self.validate(result)

        return result

    @cached_property
    def pd_result(self) -> Result:
        if not self.pd_id:
            return None

        pd_result_path = os.path.join(
            self.__class__.get_pd_result_dir(),
            self.pd_id + ".json",
        )
        pd_result_file = JSONFile(pd_result_path)
        if pd_result_file.exists:
            d = pd_result_file.read()
            return OngoingResult.from_dict(d)

        result = self.pd_result_nocache

        d = result.to_dict()
        pd_result_file.write(d)
        log.info(f"Wrote {pd_result_path}")

        return result

    @cached_property
    def timestamp(self):
        return TimeFormat("%Y-%m-%d %H:%M:%S:000").format(Time.now())
