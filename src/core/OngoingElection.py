from elections_lk import ElectionParliamentary, Result


class OngoingElection(ElectionParliamentary):
    CURRENT_YEAR = "2024"

    def __init__(self, pd_results):
        super().__init__(OngoingElection.CURRENT_YEAR)
        self.pd_results = pd_results

    @staticmethod
    def from_d_list(d_list):
        return OngoingElection([Result.from_dict(d) for d in d_list])
