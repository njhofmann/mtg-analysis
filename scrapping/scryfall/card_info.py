import requests
import json
import psycopg2
import time
from psycopg2 import sql

"""Module for pulling card info from the Scryfall API"""

# Constants
SCRYFALL_ENDPOINT = 'https://api.scryfall.com/cards/named'
SCRYFALL_ENCODING = 'utf-8'
REQUEST_DELAY = .1


def get_n_item_insert_query(n):
    """
    Returns a 'blank' SQL insert query capable of inserting n items into n columns, SQL query is wrapped around
    psycopg2's SQL builder.
    :param n: number of items query should be capable of supporting
    :return: blank SQL insert query capable of inserting n items into a table
    """
    if n < 1:
        raise ValueError('n must be greater than 0')
    columns = ' '.join(['{}' for i in range(n)])
    column_values = ', '.join(['%s' for i in range(n)])
    query = 'INSERT INTO TABLE {} ({}) VALUES ({})'.format('', columns, column_values)
    return sql.SQL(query)


def json_from_url(url):
    """
    Given a url that sends back JSON data upon a GET request, sends a GET request for it's JSON data, loads it, then
    returns it.
    :param url: url to retrieve data from
    :return: decoded JSON data from given url
    """
    time.sleep(REQUEST_DELAY)
    response = requests.get(url)
    if response.ok:
        card_data = response.content.decode(SCRYFALL_ENCODING)
        return json.loads(card_data)
    else:
        response.raise_for_status()


def get_cards_in_db(db_cursor):
    """
    Retrieves a list of all the card names that have appeared in one or more tournament level decks in the database of
    the given cursor under the 'entry_card' table.
    :param database: (String) name of the database to connect to
    :param user: (String) name of the user to retrieve data as
    :return: list of all card name that have appeared in tournament level play
    """
    card_query = sql.SQL('SELECT DISTINCT({}) FROM {}').format(
        sql.Identifier('card'), sql.Identifier('entry_card'))
    db_cursor.execute(card_query)
    return list(map(lambda x: x[0], db_cursor.fetchall()))


def get_card_data(card_name):
    """
    Retrieves the data around a given card from the Scryfall API and returns it as a dictionary.
    :param card_name: (String) name of card to retrieve data for
    :return: (dictionary) dictionary of data associated with given card
    """
    formatted_card_name = map(lambda x: x.lower(), card_name.split(' '))
    card_request_url = SCRYFALL_ENDPOINT + '?exact=' + '+'.join(formatted_card_name)
    return json_from_url(card_request_url)


def parse_and_store(card_data, db_cursor):
    """
    Given a dictionary of data for a card, from attributes to attribute values - parses the dictionary such that all
    needed info is extracted and inserted into the appropriate table in the database
    :param card_data: (JSON like dict)
    :param db_cursor: (P
    :return:
    """
    name = card_data['name']

    def check_and_add(attribute, insert_func):
        if attribute in card_data:
            insert_func(name, card_data[attribute], db_cursor)

    check_and_add('colors', insert_card_colors)
    check_and_add('cmc', insert_card_cmc)
    check_and_add('type_line', insert_card_types)
    check_and_add('text', insert_card_text)

    if 'power' in card_data and 'toughness' in card_data:
        power = card_data['power']
        toughness = card_data['toughness']
        insert_card_pt(name, power, toughness, db_cursor)

    set_search_url = card_data['prints_search_uri']
    card_printings = get_card_printings(set_search_url)
    insert_card_printings(name, card_printings, db_cursor)


def get_card_printings(set_search_url):
    """
    Given the url listing the data for every set an associated card has been printed in, returns a list of each set the
    card was printed in.
    :param set_search_url: url to retrieve card set data from
    :return: list of sets card associated with url has been printed in
    """
    json_response = json_from_url(set_search_url)
    set_data = json_response['data']
    return [card['set'] for card in set_data]


def insert_card_colors(card_name, colors, db_cursor):
    insert_query = get_n_item_insert_query(2).format(
        sql.Identifier('cards.color'), sql.Identifier('card'), sql.Identifier('color'))
    for color in colors:
        color = color.lower()
        db_cursor.execute(insert_query, (card_name, color))


def insert_card_pt(card_name, power, toughness, db_cursor):
    insert_query = get_n_item_insert_query(3).format(
        sql.Identifier('cards.pt'), sql.Identifier('card'), sql.Identifier('power'), sql.Identifier('toughness'))
    db_cursor.execute(insert_query, (card_name, power, toughness))


def insert_card_text(card_name, text, db_cursor):
    insert_query = get_n_item_insert_query(2).format(
        sql.Identifier('cards.text'), sql.Identifier('card'), sql.Identifier('text'))
    db_cursor.execute(insert_query, (card_name, text))


def insert_card_cmc(card_name, cmc, db_cursor):
    insert_query = get_n_item_insert_query(2).format(
        sql.Identifier('cards.cmc'), sql.Identifier('card'), sql.Identifier('cmc'))
    db_cursor.execute(insert_query, (card_name, cmc))


def insert_card_types(card_name, types, db_cursor):
    insert_query = get_n_item_insert_query(2).format(
        sql.Identifier('cards.type'), sql.Identifier('card'), sql.Identifier('type'))
    for card_type in types:
        db_cursor.execute(insert_query, (card_name, card_type))


def insert_card_printings(card_name, sets, db_cursor):
    insert_query = get_n_item_insert_query(2).format(
        sql.Identifier('cards.printing'), sql.Identifier('card'), sql.Identifier('set'))
    for printing in sets:
        db_cursor.execute(insert_query, (card_name, printing))


def get_stored_card_data(database, user):
    with psycopg2.connect(database=database, user=user) as conn:
        conn.autocommit = True
        with conn.cursor() as cursor:
            # get all cards stored in database
            recorded_cards = get_cards_in_db(cursor)

            # for each card get data from Scryfall, then parse and store it appropriately
            for card in recorded_cards:
                card_data = get_card_data(card)
                parse_and_store(card_data, cursor)


if __name__ == '__main__':
    #print(get_cards_in_db('mtg_analysis', 'postgres'))
    a = get_card_data('lightning bolt')
    print(parse_and_store(a, None))