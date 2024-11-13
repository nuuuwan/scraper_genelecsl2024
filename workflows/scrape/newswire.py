from scraper import NewsWire


def main():

    election = NewsWire().election
    print()
    print(election.lk_result)
    print()
    print(election.cum_party_to_seats)
    print()


if __name__ == "__main__":
    main()
