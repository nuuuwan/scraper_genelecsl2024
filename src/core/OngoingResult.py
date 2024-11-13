from elections_lk import PartyToVotes, Result, VoteSummary


class OngoingResult(Result):
    def __init__(self, id, vote_summary, party_to_votes, timestamp):
        super().__init__(id, vote_summary, party_to_votes)
        self.timestamp = timestamp

    @classmethod
    def from_dict(cls, d) -> "Result":

        d_vote_summary = dict(
            electors=d["electors"],
            polled=d["polled"],
            valid=d["valid"],
            rejected=d["rejected"],
        )

        d_party_to_votes = {}
        for k, v in d.items():
            if k in d_vote_summary or k in ["entity_id", "timestamp"]:
                continue
            d_party_to_votes[k] = v

        return cls(
            id=d["entity_id"],
            party_to_votes=PartyToVotes.from_dict(d_party_to_votes),
            vote_summary=VoteSummary.from_dict(d_vote_summary),
            timestamp=d["timestamp"],
        )

    def to_dict(self):
        d = {
            # entity
            "entity_id": self.id,
            "timestamp": self.timestamp,
            # vote_summary
            "electors": self.vote_summary.electors,
            "polled": self.vote_summary.polled,
            "valid": self.vote_summary.valid,
            "rejected": self.vote_summary.rejected,
        }
        # party_to_votes
        for party, votes in self.party_to_votes.idx.items():
            d[party] = votes
        return d
