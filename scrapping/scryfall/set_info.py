import psycopg2
from psycopg2 import sql
import scrapping.utility as su
import scrapping.scryfall.utility as ssu

"""Module for pulling set info from the Scryfall API"""


def get_sets_from_db(db_cursor):
    return ssu.get_distinct_column_from_table(db_cursor, ('cards', 'printings'), 'set')


def get_set_data(printing, logger):
    pass


def insert_set_data(printing, logger):
    pass


def get_stored_set_data(database, user, logger):
    with psycopg2.connect(database=database, user=user) as conn:
        conn.autocommit = True
        with conn.cursor() as cursor:
            # get all sets stored in database
            recorded_sets = get_sets_from_db(cursor,)

            # # for each set get data from Scryfall, then parse and store it appropriately
            # for card in recorded_sets:
            #     card_data = get_set_data(card, logger)
            #     insert_set_data()


if __name__ == '__main__':
    logger = su.init_logging('tcgplayer_api.log')
    get_stored_set_data('mtg_analysis', 'postgres', logger)