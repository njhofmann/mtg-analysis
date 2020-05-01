import json
import time
import requests
from psycopg2 import sql

"""Module for common utility functions relating to retrieving and storing Scryfall data"""

# Constants
SCRYFALL_ENCODING = 'utf-8'
REQUEST_DELAY = .1


def json_from_url(url):
    """Given a url that sends back JSON data upon a GET request, sends a GET request for it's JSON data, loads it, then
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


def get_distinct_column_from_table(db_cursor, table, column):
    """Returns all the distinct info in the given column of the given table, in the database represented by the given
    database cursor.
    :param db_cursor: cursor of the database from which to draw data
    :param table: name of the table to draw data from, expected as a list of strings to account for additional schema
    name and other preceding identifying info
    :param column: name of the column in given table to draw data from
    :return: list of all the distinct info in the given column
    """
    card_query = sql.SQL('SELECT DISTINCT({}) FROM {}').format(
        sql.Identifier(column), sql.Identifier(*table))
    db_cursor.execute(card_query)
    return [card for card in map(lambda x: x[0], db_cursor.fetchall())]


def get_n_item_insert_query(n):
    """Returns a 'blank' SQL insert query capable of inserting n items into n columns, SQL query is wrapped around
    psycopg2's SQL builder.
    :param n: number of items query should be capable of supporting
    :return: blank SQL insert query capable of inserting n items into a table
    """
    if n < 1:
        raise ValueError('n must be greater than 0')
    columns = ', '.join(['{}' for i in range(n)])
    column_values = ', '.join(['%s' for i in range(n)])
    query = 'INSERT INTO {} ({}) VALUES ({})'.format('{}', columns, column_values)
    return sql.SQL(query)


