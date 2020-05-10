import requests
import re
import datetime as dt
import multiprocessing as mp
import math as m
from typing import List, Any, Iterable, Tuple, Optional, Dict
from psycopg2 import sql
import psycopg2
import scrapping.utility as su
import database.db_reader as dbr

"""Module for pulling all the pricing data available for each card and its associated printings in the database."""

# Constants
MTGGOLDFISH_PRICING_URL = 'https://www.mtggoldfish.com/price/{}{}/{}#paper'
DATE_PRICE_PATTERN = re.compile('d \+?= "\\\\n[0-9]{4}-[0-9]{2}-[0-9]{2}, [0-9]+.[0-9]{1,2}";')
DATE_PATTERN = re.compile('[0-9]{4}-[0-9]{2}-[0-9]{2}')
PRICE_PATTERN = re.compile('[0-9]+.[0-9]{1,2}";$')
MAGIC_CORE_SET_PATTERN = re.compile('Magic 201[45]')
EDITION_PATTERN = re.compile('(Modern Masters|Planechase) [0-9]{4}')
WORKER_COUNT = 4


def get_cards_and_printings(cursor):
    """Retrieves all cards and their respective printings from the database associated with the given cursor.
    :param cursor: cursor of the database to retrieve cards and their printings from
    :return: list of tuples where each tuple is a card name, a set abbreviation, and a set
    """
    select_query = sql.SQL('SELECT {}, {}, {} FROM {} {} JOIN {} {} ON {} = {}').format(
        sql.Identifier('s', 'card'),
        sql.Identifier('s', 'set'),
        sql.Identifier('c', 'full_name'),
        sql.Identifier('cards', 'printings'),
        sql.Identifier('s'),
        sql.Identifier('cards', 'set_info'),
        sql.Identifier('c'),
        sql.Identifier('c', 'set'),
        sql.Identifier('s', 'set'))
    cursor.execute(select_query)
    return cursor.fetchall()


def insert_price_data(card, printing, price, date, is_paper, db_cursor, logger, prod_mode):
    """Inserts the given instance of price data into the database of the associated cursor. An instance of price data is
    the price for the printing of a card on a given date.
    :param card: name of card
    :param printing: set card was printed in
    :param price: cost of the card's printing
    :param date: when price was recorded
    :param is_paper: is price for a paper printing or online printing
    :param db_cursor: cursor of the database to retrieve data from
    :param logger: logger to record any relevant info with
    :return: None
    """
    def price_insert_query():
        insert_query = sql.SQL('INSERT INTO {} ({}, {}, {}, {}, {}) VALUES (%s, %s, %s, %s, %s)').format(
            sql.Identifier('prices', 'pricing'),
            sql.Identifier('card'),
            sql.Identifier('set'),
            sql.Identifier('date'),
            sql.Identifier('price'),
            sql.Identifier('is_paper'))
        db_cursor.execute(insert_query, (card, printing, date, price, is_paper))

    warning_msg = f'Duplicate price insertion into prices.printing for card {card} from printing {printing} on {date}'
    logger.info(f'Inserting card price for card {card}, printing {printing} on {date}')
    su.execute_query(price_insert_query, logger, warning_msg, prod_mode)


def get_mtggoldfish_pricing_url(printing, card, foil):
    """Returns a MTGGoldFish url, that in theory, should return a webpage for the given card printing.
    :param printing: set card was printed in
    :param card: name of the card
    :param foil: if card printing is foil
    :return: MTGGoldfish url for the given card printing"""

    def rejoin_on_plus(string):
        return '+'.join(string.split(' '))

    printing = rejoin_on_plus(printing)
    card = rejoin_on_plus(card)
    foil_str = ':Foil' if foil else ''
    return MTGGOLDFISH_PRICING_URL.format(printing, foil_str, card)


def format_printing_name(printing: str) -> str:
    """Formats the name of a MTG set so it can be used in a MTGGoldFish url.
    :param printing: name of the set to format
    :return: formatted printing name
    """
    printing = format_for_url(printing)
    if printing == 'Modern Masters 2015':
        return printing
    elif EDITION_PATTERN.match(printing) or 'Commander 2013' == printing:
        return printing + ' Edition'
    elif MAGIC_CORE_SET_PATTERN.match(printing):
        return printing + ' Core Set'
    elif 'Commander 2011' == printing:
        return 'Commander'
    return printing


def format_for_url(name: str) -> str:
    """Formats the given text so it can be used in a MTGoldFish url by removing all commas, apostrophes, forwards
    slashes, periods, and colons
    :param name: card name to format
    :return: formatted card name
    """
    return ''.join(map(lambda x: '' if x in ("'", ',', ':', '/', '.') else x, name))


def get_mtggoldfish_data(name: str, printing_abbrv: str, printing: str, logger) -> Optional[str]:
    """Retrieves HTTP text from MTGGoldFish webpage for the printing of the given card, if such a webpage exists - else
     returns None. Attempts several different URLs.
    :param name: name of the card to retrieve
    :param printing_abbrv: abbreviation of the card's printing
    :param printing: printing of the card to retrieve data for
    :param logger: logger to record any relevant information
    :return: HTTP text of the card's printing on MTGGoldfish, or None
    """
    formatted_name = format_for_url(name)
    formatted_printing = format_printing_name(printing)

    # try printing non-foil, printing code non foil, printing foil, printing code foil
    urls = [(get_mtggoldfish_pricing_url(formatted_printing, formatted_name, False), 'printing, non-foil'),
            (get_mtggoldfish_pricing_url(printing_abbrv, formatted_name, False), 'printing abbreviation, non-foil'),
            (get_mtggoldfish_pricing_url(formatted_printing, formatted_name, True), 'printing, foil'),
            (get_mtggoldfish_pricing_url(printing_abbrv, formatted_name, True), 'printing abbreviation, foil')]

    for url, msg in urls:
        response = requests.get(url)
        if response.ok:
            logger.info(f'Got data for card {name} from {url} with parameters {msg}')
            return response.text

    logger.error(f'Failed to fetch prices for card {name} for printing {printing}')
    return None


def get_printing_prices(card_name: str, printing_code: str, printing: str, logger) \
        -> Tuple[Optional[Dict[str, str]], Optional[Dict[str, str]]]:
    """Retrieves all prices for the given card printing, trying multiple different possible urls. Returns two
    dictionaries of dates to prices, one for paper printings and one for online printings. If dict is empty, no prices
    were retrieved.
    :param card_name: name of the card to retrieve prices for
    :param printing_code: abbreviation of the printing from which prices are being retrieved for
    :param printing: printing from which prices are being retrieved for
    :param logger: logger to record any useful information
    :return: dictionaries of dates to prices for any retrieved prices, for paper and online prices
    """
    # try printing non-foil printing code non foil, printing foil, printing code foil
    data = get_mtggoldfish_data(card_name, printing_code, printing, logger)

    if not data:  # no data fetched, terminate early
        return {}, {}

    matches = DATE_PRICE_PATTERN.findall(data)

    # separate paper and online prices, paper prices first
    paper_prices = {}
    online_prices = {}
    prev_date = None
    for match in matches:
        date = DATE_PATTERN.search(match).group(0)
        parsed_date = dt.datetime.strptime(date, '%Y-%m-%d')
        price = PRICE_PATTERN.search(match).group(0)[:-2]  # get rid of "; in regex pattern

        # dates listed past to current in two groups for paper and online, when date "jumps down", have switched to
        # the second (online) group
        if prev_date is None or parsed_date > prev_date:
            prev_date = parsed_date
            paper_prices[date] = price
        else:
            online_prices[date] = price

    return paper_prices, online_prices


def divide_list(lst: List[Any], n: int) -> List[List[Any]]:
    """Divides the given list into n even sized chunks (rounding up).
    :param lst: list to divide
    :param n: number of chunks
    :return: divided list
    """
    n = m.ceil(len(lst) / n)
    return [lst[i:i + n] for i in range(0, len(lst), n)]


def get_and_store_prices(database: str, user: str, prod_mode: bool) -> None:
    """For each card and its associated printings currently stored in the database, attempts to retrieve prices for each
    card and printing pairing - then store them in the database.
    :param database: name of the database
    :param user: username to login into the database with
    :param prod_mode: boolean signifying production or testing mode
    :return: None
    """
    def process(process_id: int, entries: List[Tuple[str, str, str]]) -> None:
        # find prices for each one
        logger = su.init_logging(f'mtgtop8_scrapper_{process_id}.log')
        try:
            for name, printing_code, printing in entries:
                paper_prices, online_prices = get_printing_prices(name, printing_code, printing, logger)

                # insert each price into database
                for mapping, is_paper in ((paper_prices, True), (online_prices, False)):
                    for date, price in mapping.items():
                        insert_price_data(name, printing_code, price, date, is_paper, cursor, logger, prod_mode)
        except Exception as e:
            if prod_mode:
                logger.warning(str(e))
            else:
                raise e

    with psycopg2.connect(database=database, user=user) as conn:
        conn.autocommit = True
        with conn.cursor() as cursor:
            db_entries = get_cards_and_printings(cursor)

    chunked_entries = divide_list(db_entries, WORKER_COUNT)
    processes = [mp.Process(target=process, args=(i, chunked_entries[i])) for i in range(WORKER_COUNT)]

    for process in processes:
        process.start()

    for process in processes:
        process.join()


def main(prod_mode: bool) -> None:
    get_and_store_prices(dbr.DATABASE_NAME, dbr.USER, prod_mode)


if __name__ == '__main__':
    main(False)
