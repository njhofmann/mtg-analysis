import psycopg2
import sys
from psycopg2 import sql
import database.db_reader as r


"""Module for creating a new instance of the database this project interpoles with"""


def create_new_db(db_schema: str, replace_existing: bool) -> None:
    """Creates a new instance of a this project's database, using the information from this project's config file and
    the given database schema. Note the option to replace any existing database with the name the created database will
    be given (i.e. prior versions of this project's database).
    :param db_schema: path to the schema file of the database
    :param replace_existing: whether or not to replace a database with the name the new database will be initalized with
    :return: None
    """
    # create connection, set isolation level to create db, and create cursor
    with psycopg2.connect(user=r.USER, password=r.PASSWORD) as con:
        con.autocommit = True
        with con.cursor() as cursor:
            # remove all other active sessions
            remove_query = sql.SQL('SELECT pg_terminate_backend(pg_stat_activity.pid) '
                                   'FROM pg_stat_activity WHERE pg_stat_activity.datname = {}  pg_backend_pid()'.
                                   format(sql.Identifier(r.DATABASE_NAME)))
            cursor.execute(remove_query)

            # delete database if it exists, create new one from init file
            if replace_existing:
                cursor.execute(sql.SQL('DROP DATABASE IF EXISTS {}').format(sql.Identifier(r.DATABASE_NAME)))
            cursor.execute(sql.SQL('CREATE DATABASE {}').format(sql.Identifier(r.DATABASE_NAME)))

    # open connection to new database and insert schema
    with psycopg2.connect(user=r.USER, password=r.PASSWORD, dbname=r.DATABASE_NAME) as con:
        with con.cursor() as cursor:
            with open(db_schema) as init:
                schema = ''.join([line.strip() for line in init.readlines()])
            cursor.execute(schema)
            con.commit()


if __name__ == '__main__':
    if len(sys.argv) < 3:
        raise ValueError(f'usage {sys.argv[0]} blank_or_full_schema replace_if_existing')

    if sys.argv[1] in ('true', 't'):
        blank_or_full = True
    elif sys.argv[1] in ('false', 'f'):
        blank_or_full = False
    else:
        raise ValueError('blank_or_full_schema: true / t, false / f')

    if sys.argv[2] in ('true', 't'):
        replace_existing = True
    elif sys.argv[2] in ('false', 'f'):
        replace_existing = False
    else:
        raise ValueError('replace_existing: true / t, false / f')

    init_schema = 'schema.sql' if blank_or_full else 'db_backup.sql'
    create_new_db(init_schema, replace_existing)
