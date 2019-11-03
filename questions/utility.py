import database.db_reader as ddr
import psycopg2

def generic_search(search_query):
    """
    Generic function that executes a search query in the database and returns the results.
    :param search_query: search query to execute
    :return: results of search query
    """
    with psycopg2.connect(user=ddr.USER, database=ddr.DATABASE_NAME) as con:
        with con.cursor() as cursor:
            cursor.execute(search_query)
            return cursor.fetchall()


if __name__ == '__main__':
    print(generic_search('SELECT * FROM events.event_entry LIMIT 10'))