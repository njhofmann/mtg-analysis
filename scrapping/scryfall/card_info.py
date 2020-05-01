import scrapping.scryfall.utility as ssu
import psycopg2
import scrapping.utility as su
from psycopg2 import sql
import database.db_reader as dbr

"""Module for pulling card info from the Scryfall API"""

# Constants
SCRYFALL_ENDPOINT = 'https://api.scryfall.com/cards/named'
INVALID_CARDS = ['Unknown Card']
INVALID_TYPES = ['-', '//', 'ù']


def get_cards_in_db(db_cursor, logger):
    """Retrieves a list of all the card names that have appeared in one or more tournament level decks in the database
    of the given cursor under the 'entry_card' table.
    :param: db_cursor:
    :param: logger:
    :return: list of all card name that have appeared in tournament level play
    """
    logger.info(msg='Getting list of cards to retrieve info for')
    card_query = sql.SQL('SELECT DISTINCT({}) FROM {}').format(
        sql.Identifier('card'),
        sql.Identifier('events', 'entry_card'))
    db_cursor.execute(card_query)
    return [card for card in map(lambda x: x[0], db_cursor.fetchall()) if card not in INVALID_CARDS]


def get_card_data(card_name, logger):
    """Retrieves the data around a given card from the Scryfall API and returns it as a dictionary.
    :param card_name: (String) name of card to retrieve data for
    :return: (dictionary) dictionary of data associated with given card
    """
    logger.info(msg=f'Retrieving data for card {card_name}')
    formatted_card_name = map(lambda x: x.lower(), card_name.split(' '))
    card_request_url = SCRYFALL_ENDPOINT + '?exact=' + '+'.join(formatted_card_name)
    return ssu.json_from_url(card_request_url)


def parse_and_store(card_data, db_cursor, logger, prod_mode):
    """Given a dictionary of data for a card, from attributes to attribute values - parses the dictionary such that all
    needed info is extracted and inserted into the appropriate table in the database
    :param card_data: (JSON like dict)
    :param db_cursor: (P
    :return:"""
    name = card_data['name']

    def check_and_add(attribute, insert_func):
        if attribute in card_data:
            insert_func(name, card_data[attribute], db_cursor, logger, prod_mode)

    check_and_add('cmc', insert_card_cmc)
    check_and_add('type_line', insert_card_types)
    check_and_add('oracle_text', insert_card_text)

    if 'colors' not in card_data:
        card_data['colors'] = ['c']
    check_and_add('colors', insert_card_colors)

    if 'power' in card_data and 'toughness' in card_data:
        power = card_data['power']
        toughness = card_data['toughness']
        insert_card_pt(name, power, toughness, db_cursor, logger, prod_mode)

    set_search_url = card_data['prints_search_uri']
    card_printings = get_card_printings(set_search_url)
    insert_card_printings(name, card_printings, db_cursor, logger, prod_mode)


def get_card_printings(set_search_url):
    """Given the url listing the data for every set an associated card has been printed in, returns a list of each set
    the card was printed in.
    :param set_search_url: url to retrieve card set data from
    :return: list of sets card associated with url has been printed in
    """
    json_response = ssu.json_from_url(set_search_url)
    set_data = json_response['data']
    return set([card['set'] for card in set_data])


def insert_card_colors(card_name, colors, db_cursor, logger, prod_mode):
    for color in colors:
        def insert_query():
            insert_query = ssu.get_n_item_insert_query(2).format(
                sql.Identifier('cards', 'colors'),
                sql.Identifier('card'),
                sql.Identifier('color'))
            db_cursor.execute(insert_query, (card_name, color.lower()))

        logger.info(f'Inserting color {color} for card {card_name}')
        warning_msg = f'Duplicate entry for card {card_name} with color {color}'
        su.execute_query(insert_query, logger, warning_msg, prod_mode)


def insert_card_pt(card_name, power, toughness, db_cursor, logger, prod_mode):
    def insert_query():
        insert_query = ssu.get_n_item_insert_query(3).format(
            sql.Identifier('cards', 'pt'),
            sql.Identifier('card'),
            sql.Identifier('power'),
            sql.Identifier('toughness'))
        db_cursor.execute(insert_query, (card_name, power, toughness))

    logger.info(msg=f'Inserting power {power}, toughness {toughness} info for card {card_name}')
    warning_msg = f'Duplicate entry for for card {card_name} for power {power}, toughness {toughness}'
    su.execute_query(insert_query, logger, warning_msg, prod_mode)


def insert_card_text(card_name, text, db_cursor, logger, prod_mode):
    def insert_query():
        insert_query = ssu.get_n_item_insert_query(2).format(
            sql.Identifier('cards', 'text'),
            sql.Identifier('card'),
            sql.Identifier('text'))
        db_cursor.execute(insert_query, (card_name, text))

    logger.info(msg=f'Inserting card text for card {card_name}')
    warning_msg = f'Duplicate entry for card {card_name} and associated text'
    su.execute_query(insert_query, logger, warning_msg, prod_mode)


def insert_card_cmc(card_name, cmc, db_cursor, logger, prod_mode):
    def insert_query():
        insert_query = ssu.get_n_item_insert_query(2).format(
            sql.Identifier('cards', 'cmc'),
            sql.Identifier('card'),
            sql.Identifier('cmc'))
        db_cursor.execute(insert_query, (card_name, cmc))

    logger.info(msg=f'Inserting cmc {cmc} for card {card_name}')
    warning_msg = f'Duplicate entry for card {card_name} and cmc {cmc}'
    su.execute_query(insert_query, logger, warning_msg, prod_mode)


def insert_card_types(card_name, type_line, db_cursor, logger, prod_mode):
    types = [card_type.lower() for card_type in type_line.split(' ') if card_type not in INVALID_TYPES]
    for card_type in types:
        if card_type != '—':
            def insert_query():
                insert_query = ssu.get_n_item_insert_query(2).format(
                    sql.Identifier('cards', 'types'),
                    sql.Identifier('card'),
                    sql.Identifier('type'))
                db_cursor.execute(insert_query, (card_name, card_type))

            logger.info(msg=f'Inserting type {card_name} for card {card_name}')
            warning_msg = f'Duplicate entry for card {card_name} with type {card_type}'
            su.execute_query(insert_query, logger, warning_msg, prod_mode)


def insert_card_printings(card_name, sets, db_cursor, logger, prod_mode):
    for printing in sets:
        def insert_query():
            insert_query = ssu.get_n_item_insert_query(2).format(
                sql.Identifier('cards', 'printings'),
                sql.Identifier('card'),
                sql.Identifier('set'))
            db_cursor.execute(insert_query, (card_name, printing))

        logger.info(msg=f'Inserting printing {printing} for card {card_name}')
        warning_msg = f'Duplicate entry for card {card_name} and printing {printing}'
        su.execute_query(insert_query, logger, warning_msg, prod_mode)


def get_stored_card_data(database, user, logger, prod_mode):
    with psycopg2.connect(database=database, user=user) as conn:
        conn.autocommit = True
        with conn.cursor() as cursor:
            # get all cards stored in database
            recorded_cards = get_cards_in_db(cursor, logger)

            # for each card get data from Scryfall, then parse and store it appropriately
            for card in recorded_cards:
                card_data = get_card_data(card, logger)
                parse_and_store(card_data, cursor, logger, prod_mode)


def main(prod_mode):
    logger = su.init_logging('scryfall_card_scapper.log')
    get_stored_card_data(dbr.DATABASE_NAME, dbr.USER, logger, prod_mode)


if __name__ == '__main__':
    main(False)
