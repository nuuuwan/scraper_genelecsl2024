import os

from utils import JSONFile, Log, TSVFile

from scraper import ECLK

log = Log("CommonLocalState")


class CommonLocalState:
    DATA_TSV_PATH = ECLK.get_election_path()
    COMMON_LOCAL_STATE_PATH = os.path.join(
        "data", "common_local_state", "common_local_state.json"
    )
    COMMON_LOCAL_STATE_FILE = JSONFile(COMMON_LOCAL_STATE_PATH)

    def __init__(self, n_results_display):
        self.n_results_display = n_results_display

    def __str__(self):
        return f"CommonLocalState(n_results_display={self.n_results_display})"

    def to_dict(self):
        return dict(n_results_display=self.n_results_display)

    @staticmethod
    def from_dict(d):
        return CommonLocalState(n_results_display=d["n_results_display"])

    def store(self):
        CommonLocalState.COMMON_LOCAL_STATE_FILE.write(self.to_dict())
        log.info(f"Wrote {CommonLocalState.COMMON_LOCAL_STATE_PATH}")

    @staticmethod
    def load():
        if not CommonLocalState.COMMON_LOCAL_STATE_FILE.exists:
            return None
        d = CommonLocalState.COMMON_LOCAL_STATE_FILE.read()
        return CommonLocalState.from_dict(d)

    @staticmethod
    def update():
        data_list = TSVFile(CommonLocalState.DATA_TSV_PATH).read()
        n_results_display_new = len(data_list)

        common_local_state = CommonLocalState.load()
        if common_local_state:

            if n_results_display_new <= common_local_state.n_results_display:
                log.error(
                    f"❌ No data gain: {n_results_display_new}"
                    + f" <= {common_local_state.n_results_display}"
                )
                raise Exception("No data gain")

        common_local_state = CommonLocalState(
            n_results_display=n_results_display_new
        )
        common_local_state.store()
        log.info(f"Updated: {common_local_state}")
        return common_local_state


if __name__ == "__main__":
    CommonLocalState.update()
