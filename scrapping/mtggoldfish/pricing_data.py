import requests
import re
import datetime as dt
from psycopg2 import sql
import psycopg2
import scrapping.utility as su

"""Module for pulling all the pricing data available for each card and its associated printings in the database."""

# Constants
MTGGOLDFISH_PRICING_URL = 'https://www.mtggoldfish.com/price/{}{}/{}#paper'
DATE_PRICE_PATTERN = re.compile('d \+?= "\\\\n[0-9]{4}-[0-9]{2}-[0-9]{2}, [0-9]+.[0-9]{1,2}";')
DATE_PATTERN = re.compile('[0-9]{4}-[0-9]{2}-[0-9]{2}')
PRICE_PATTERN = re.compile('[0-9]+.[0-9]{1,2}";$')


def get_cards_and_printings(cursor):
    select_query = sql.SQL('SELECT {}, {}, {} FROM {} {} JOIN {} {} ON {} = {}').format(
        sql.Identifier('s', 'card'), sql.Identifier('s', 'set'), sql.Identifier('c', 'full_name'),
        sql.Identifier('cards', 'printings'), sql.Identifier('s'), sql.Identifier('cards', 'set_info'),
        sql.Identifier('c'), sql.Identifier('c', 'set'), sql.Identifier('s', 'set'))
    cursor.execute(select_query)
    return cursor.fetchall()


def insert_price_data(card, printing, price, date, is_paper, db_cursor, logger):
    def price_insert_query():
        insert_query = sql.SQL('INSERT INTO {} VALUES ({}, {}, {}, {})').format(
            sql.Identifier('prices', 'pricing'), sql.Identifier('card'), sql.Identifier('set'), sql.Identifier('date'),
            sql.Identifier('price'), sql.Identifier('is_paper'))
        db_cursor.execute(insert_query, (card, printing, date, price, is_paper))

    warning_msg = 'Duplicate price insertion into {} for card {} from printing {} on {}'.format(
        'prices.printing', 'card', 'printing', 'date')
    su.execute_query_pass_on_unique_violation(price_insert_query, logger, warning_msg)


def get_mtggoldfish_pricing_url(printing, card, foil):
    def rejoin_on_plus(string):
        return '+'.join(string.split(' '))

    printing = rejoin_on_plus(printing)
    card = rejoin_on_plus(card)
    foil_str = ':Foil' if foil else ''
    return MTGGOLDFISH_PRICING_URL.format(printing, foil_str, card)

def get_mtggoldfish_data(name, printing_abbrv, printing, logger):
    formatted_name = name.replace("'", '')  # get rid of quotes

    # try printing non-foil, printing code non foil, printing foil, printing code foil
    urls = [(get_mtggoldfish_pricing_url(printing, formatted_name, False), 'printing, non-foil'),
            (get_mtggoldfish_pricing_url(printing_abbrv, formatted_name, False), 'printing abbreviation, non-foil'),
            (get_mtggoldfish_pricing_url(printing, formatted_name, True), 'printing, foil'),
            (get_mtggoldfish_pricing_url(printing_abbrv, formatted_name, True), 'printing abbreviation, foil')]

    for url, msg in urls:
        response = requests.get(url)

        if response.ok:
            logger.info(f'Got data for card {name} from {url} with parameters {msg}')
            return response.text

    logger.error(f'Failed to fetch prices for card {name} for printing {printing}')
    return None


def get_printing_prices(card_name, printing_code, printing, logger):
    # try printing non-foil printing code non foil, printing foil, printing code foil
    data = get_mtggoldfish_data(card_name, printing_code, printing, logger)

    if not data:  # no data fetched, terminate early
        return [], []

    matches = DATE_PRICE_PATTERN.findall(data)

    paper_prices = {}
    online_prices = {}
    prev_date = None
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


def get_and_store_prices(database, user, logger):
    # all cards and printings in db
    with psycopg2.connect(database=database, user=user) as conn:
        conn.autocommit = True
        with conn.cursor() as cursor:
            db_entries = get_cards_and_printings(cursor)
            # find prices for each one
            for name, printing_code, printing in db_entries:
                paper_prices, online_prices = get_printing_prices(name, printing_code, printing, logger)

                for mapping, is_paper in ((paper_prices, True), (online_prices, False)):
                    if mapping:  # check isn't empty list
                        for price, date in mapping.items():
                            print(name, printing, price)
                            #insert_price_data(name, printing_code, price, date, is_paper, cursor, logger)



if __name__ == '__main__':
    logger = su.init_logging('mtggoldfish_log.log')
    get_and_store_prices('mtg_analysis', 'postgres', logger)
    # get_printing_prices('v13', 'Future Sight', 'Tarmogoyf')
