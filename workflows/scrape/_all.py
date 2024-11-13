from scraper import ECLK, AdaDerana, NewsWire


def main():  # noqa

    first_election = None
    for Scraper in [ECLK, AdaDerana, NewsWire]:
        print("-" * 40)
        print(Scraper.__name__)
        print("-" * 40)
        election = Scraper().election
        print(election.lk_result)
        print(election.cum_party_to_seats)

        if first_election is None:
            first_election = election
        else:
            some_errors = False

            for get_value, label in [
                (
                    lambda x: x.lk_result.vote_summary.electors,
                    "vote_summary.electors",
                ),
                (
                    lambda x: x.lk_result.vote_summary.valid,
                    "vote_summary.valid",
                ),
                (lambda x: x.cum_party_to_seats, "cum_party_to_seats"),
                (lambda x: x.lk_result, "lk_result"),
            ]:
                if get_value(election) != get_value(first_election):
                    print(f"❌ [{Scraper.__name__}] {label} is different")
                    some_errors = True
                else:
                    print(f"✅ [{Scraper.__name__}] {label} is the same")

            if not some_errors:
                print(f"✅✅ [{Scraper.__name__}] ALL Validations PASSED")


if __name__ == "__main__":
    main()
