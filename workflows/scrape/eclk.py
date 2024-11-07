from scraper import ECLK


def main():
    ECLK().election
    election = ECLK().election
    print()
    print(election.lk_result)
    print()
    print(election.cum_party_to_seats)
    print()


if __name__ == "__main__":
    main()
