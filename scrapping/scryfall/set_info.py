import psycopg2
from psycopg2 import sql

import database.db_reader as dbr
import scrapping.scryfall.utility as ssu
import scrapping.utility as su

"""Module for pulling set info from the Scryfall API"""

# Constants
SCRYFALL_SET_URL = 'https://api.scryfall.com/sets'
MISSING_SETS = ('pdp11', 'psld')  # TODO sets that are currently erroring in the API


def get_sets_from_db(db_cursor):
    return ssu.get_distinct_column_from_table(db_cursor, ('cards', 'printings'), 'set')


def get_set_data(logger):
    logger.info('Retrieving all set info from Scryfall')
    json_data = ssu.json_from_url(SCRYFALL_SET_URL)
    return {printing['code']: printing for printing in json_data['data']}


def insert_set_data(db_cursor, code, full_name, release_date, size, logger, prod_mode):
    logger.info(f'Inserting set info for set {code}')

    def temp():
        insert_query = ssu.get_n_item_insert_query(4).format(
            sql.Identifier('cards', 'set_info'),
            sql.Identifier('set'),
            sql.Identifier('full_name'),
            sql.Identifier('release'),
            sql.Identifier('size'))
        db_cursor.execute(insert_query, (code, full_name, release_date, size))

    su.execute_query(temp, logger, 'failed to retrieve set info', prod_mode)


def get_stored_set_data(database, user, logger, prod_mode):
    with psycopg2.connect(database=database, user=user) as conn:
        conn.autocommit = True
        with conn.cursor() as cursor:
            # get all sets stored in database
            recorded_sets = get_sets_from_db(cursor)

            # get all set data as mapping of set code to set info
            set_data = get_set_data(logger)

            # for each set get data from Scryfall, then parse and store it appropriately
            for printing in recorded_sets:
                if printing not in set_data:  # should never happen, likely an API error or change
                    raise ValueError(f'Unsupported printing with code {printing}')

                info = set_data[printing]
                full_name = info['name']
                release_data = info['released_at']  # already in isodate form, year-month-day
                size = info['card_count']
                insert_set_data(cursor, printing, full_name, release_data, size, logger, prod_mode)



def main(prod_mode):
    logger = su.init_logging('scryfall_set_scrapper.log')
    get_stored_set_data(dbr.DATABASE_NAME, dbr.USER, logger, prod_mode)


if __name__ == '__main__':
    main(False)
