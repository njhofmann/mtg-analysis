import requests
import re

"""Module for pulling all the pricing data available for each card and its associated printings in the database."""

# Constants
MTGGOLDFISH_PRICING_URL = 'https://www.mtggoldfish.com/price/{}{}/{}#paper'
DATE_PRICE_PATTERN = re.compile('d \+?= "\n[0-9]{4}-[0-9]{2}-[0-9]{2}, [0-9]+.[0-9]{1,2}";')

def get_mtggoldfish_pricing_url(printing, card, foil):

    def rejoin_on_plus(string):
        return '+'.join(string.split(' '))

    printing = rejoin_on_plus(printing)
    card = rejoin_on_plus(card)

    if foil:
        return MTGGOLDFISH_PRICING_URL.format(printing, ':Foil', card)
    return MTGGOLDFISH_PRICING_URL.format(printing, '', card)

def get_printing_prices(printing_code, printing, card_name):
    url = get_mtggoldfish_pricing_url(printing, card_name, False)
    response = requests.get(url)

    if not response.ok:
        response.raise_for_status()

    data = response.text
    print(data)
    matches = DATE_PRICE_PATTERN.findall(data)

    # separate out paper and online prices
    print(matches)


if __name__ == '__main__':
    get_printing_prices('v13', 'Commander 2018', 'Great Furnace')
