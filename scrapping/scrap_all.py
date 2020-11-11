import scrapping.mtggoldfish.pricing_data as p
import scrapping.mtgtop8.event_data as e
import scrapping.scryfall.card_info as c
import scrapping.scryfall.set_info as s

"""Module for running each scrapper in the correct order"""


def main():
    prod_mode = True

    print('getting event data')
    e.main(prod_mode)

    print('getting set and card data')
    s.main(prod_mode)
    c.main(prod_mode)

    print('getting pricing data')
    p.main(prod_mode)


if __name__ == '__main__':
    main()
