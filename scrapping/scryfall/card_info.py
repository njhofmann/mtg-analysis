import requests
import json
import psycopg2
from psycopg2 import sql
"""Module for pulling card info from the Scryfall API"""

SCRYFALL_ENDPOINT = 'https://api.scryfall.com/cards/named'
SCRYFALL_ENCODING = 'utf-8'
REQUEST_DELAY = .1


def get_cards_in_db(database, user):
    """
    Retrieves a list of all the card names that have appeared in one or more tournament level decks in the given
    database under the 'entry_card' table.
    :param database: (String) name of the database to connect to
    :param user: (String) name of the user to retrieve data as
    :return: list of all card name that have appeared in tournament level play
    """

    with psycopg2.connect(database=database, user=user) as conn:
        with conn.cursor() as cursor:
            card_query = sql.SQL('SELECT DISTINCT({}) FROM {}').format(
                sql.Identifier('card'), sql.Identifier('entry_card'))
            cursor.execute(card_query)
            conn.commit()
            return list(map(lambda x: x[0], cursor.fetchall()))


def get_card_data(card_name):
    """
    Retrieves the data around a given card from the Scryfall API and returns it as a dictionary.
    :param card_name: (String) name of card to retrieve data for
    :return: (dictionary) dictionary of data associated with given card
    """
    formatted_card_name = map(lambda x: x.lower(), card_name.split(' '))
    card_request_url = SCRYFALL_ENDPOINT + '?exact=' + '+'.join(formatted_card_name)
    response = requests.get(card_request_url)

    if response.ok:
        card_data = response.content.decode(SCRYFALL_ENCODING)
        return json.loads(card_data)
    else:
        response.raise_for_status()


def parse_and_store(card_data):
    """
    Given a dictionary of data for a card, from attributes to attribute values - parses the dictionary such that all
    needed info is extracted and inserted into the appropriate table in the database
    :param card_data:
    :return:
    """
    name = card_data['name']

    def check_and_add(attribute, insert_func):
        if attribute in card_data:
            insert_func(name, card_data[attribute])

    check_and_add('colors', insert_card_colors)
    check_and_add('cmc', insert_card_cmc)
    check_and_add('type_line', insert_card_types)

    if 'power' in card_data and 'toughness' in card_data:
        power = card_data['power']
        toughness = card_data['toughness']
        insert_card_pt(name, power, toughness)



def insert_card_colors(card_name, colors):
    pass

def insert_card_pt(card_name, power, toughness):
    pass

def insert_card_cmc(card_name, cmc):
    pass

def insert_card_types(card_name, types):
    pass

def insert_card_printings(card_name, sets):
    pass


if __name__ == '__main__':
    #print(get_cards_in_db('mtg_analysis', 'postgres'))
    print(get_card_data('lightning bolt'))