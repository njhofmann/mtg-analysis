import psycopg2
import sys
from psycopg2 import sql


def create_new_db(db_name, init_file, user='postgres'):
    """
    Creates a new instance of a database of the given name, using the schemas in the given initialization file. Deletes
    any existing files that match the given name.
    :param db_name: name of the database
    :param init_file: path to the initialization file
    :param user:
    :return: None
    """
    # create connection, set isolation level to create db, and create cursor
    with psycopg2.connect(user=user) as con:
        con.autocommit = True
        with con.cursor() as cursor:
            # remove all other active sessions

            # delete database if it exists, create new one from init file
            cursor.execute(sql.SQL('DROP DATABASE IF EXISTS {}').format(sql.Identifier(db_name)))
            cursor.execute(sql.SQL('CREATE DATABASE {}').format(sql.Identifier(db_name)))
            con.commit()

    # open connection to new database and insert schema
    with psycopg2.connect(user=user, dbname=db_name) as con:
        with con.cursor() as cursor:
            with open(init_file) as init:
                schema = ''.join([line.strip() for line in init.readlines()])
                cursor.execute(schema)
                con.commit()


if __name__ == '__main__':
    create_new_db('mtg_analysis', 'database_schema.txt')
