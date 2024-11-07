from scraper import AdaDerana


def main():

    election = AdaDerana().election
    print()
    print(election.lk_result)
    print()
    print(election.cum_party_to_seats)
    print()


if __name__ == "__main__":
    main()
