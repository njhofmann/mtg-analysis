import scrapping.mtggoldfish.pricing_data as p
import scrapping.scryfall.set_info as s
import scrapping.scryfall.card_info as c
import scrapping.mtgtop8.event_data as e

"""Module for running each scrapper in the correct order"""


def main():
    print('getting event data')
    e.main()

    print('getting set and card data')
    s.main()
    c.main()

    print('getting pricing data')
    p.main()


if __name__ == '__main__':
    main()
