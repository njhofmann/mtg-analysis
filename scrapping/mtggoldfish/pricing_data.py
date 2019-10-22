import requests
import re
import datetime as dt

"""Module for pulling all the pricing data available for each card and its associated printings in the database."""

# Constants
MTGGOLDFISH_PRICING_URL = 'https://www.mtggoldfish.com/price/{}{}/{}#paper'
DATE_PRICE_PATTERN = re.compile('d \+?= "\\\\n[0-9]{4}-[0-9]{2}-[0-9]{2}, [0-9]+.[0-9]{1,2}";')
DATE_PATTERN = re.compile('[0-9]{4}-[0-9]{2}-[0-9]{2}')
PRICE_PATTERN = re.compile('[0-9]+.[0-9]{1,2}";$')


def get_cards_and_printings():
    pass


def insert_price_data(price, date, is_paper):
    pass


def get_mtggoldfish_pricing_url(printing, card, foil):

    def rejoin_on_plus(string):
        return '+'.join(string.split(' '))

    printing = rejoin_on_plus(printing)
    card = rejoin_on_plus(card)

    if foil:
        return MTGGOLDFISH_PRICING_URL.format(printing, ':Foil', card)
    return MTGGOLDFISH_PRICING_URL.format(printing, '', card)


def get_printing_prices(printing_code, printing, card_name):

    # try printing non-foil, printing code non foil, printing foil, printing code foil

    url = get_mtggoldfish_pricing_url(printing, card_name, False)
    response = requests.get(url)

    if not response.ok:
        response.raise_for_status()

    data = response.text
    print(data)
    matches = DATE_PRICE_PATTERN.findall(data)

    paper_prices = {}
    online_prices = {}
    prev_date = None
    print(matches)
    # separate paper and online prices, paper prices first
    for match in matches:
        date = DATE_PATTERN.search(match).group(0)
        parsed_date = dt.datetime.strptime(date, '%Y-%m-%d')
        price = PRICE_PATTERN.search(match).group(0)[:-2]  # get rid of "; in regex pattern

        if prev_date is None or parsed_date > prev_date:
            prev_date = parsed_date
            paper_prices[date] = price
        else:
            online_prices[date] = price

    return paper_prices, online_prices


def get_and_store_prices():
    # all cards and printings in db
    # find prices for each one
    # insert
    paper_prices, online_prices = get_printing_prices()

    for mapping, is_paper in ((paper_prices, True), (online_prices, False)):
        if mapping:
            for price, date in mapping.items():
                insert_price_data(price, date, is_paper)


if __name__ == '__main__':
    get_printing_prices('v13', 'Future Sight', 'Tarmogoyf')
