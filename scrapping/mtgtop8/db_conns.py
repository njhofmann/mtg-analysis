from psycopg2 import sql
import scrapping.utility as su

"""Module for inserting tournament data from mtgtop8.com."""


def insert_into_tournament_info(event_name, event_date, event_format, event_url, db_cursor, logger):
    """Inserts info for a tournament into the cursor of the given database. Assume size is None for now, can be lated
    updated if needed
    :param event_name: name of tournament
    :param event_date: date tournament was held
    :param event_format: format tournament was played in
    :param event_url: url from which tournament info was pulled from
    :param db_cursor: cursor of the database where info will be pushed
    :param logger: logger by which info will be logged
    :return: None"""

    def insert_query_func():
        insert_query = sql.SQL('INSERT INTO {} ({}, {}, {}, {}) VALUES (%s, %s, %s, %s)').format(
            sql.Identifier('events', 'event_info'),
            sql.Identifier('name'),
            sql.Identifier('date'),
            sql.Identifier('format'),
            sql.Identifier('url'))
        db_cursor.execute(insert_query, (event_name, event_date, event_format, event_url))

    warning_msg = f'Duplicate entry for tournament_info attempted, key {event_name}, {event_date}'
    su.execute_query_pass_on_unique_violation(insert_query_func, logger, warning_msg)


def get_tournament_info_id(event_name, event_date, event_format, event_url, db_cursor):
    """
    :param event_name:
    :param event_date:
    :param event_format:
    :param event_url:
    :param db_cursor:
    :return:"""
    tourny_id_query = sql.SQL('SELECT {} FROM {} WHERE {} = %s AND {} = %s AND {} = %s AND {} = %s').format(
        sql.Identifier('tourny_id'),
        sql.Identifier('events', 'event_info'),
        sql.Identifier('name'),
        sql.Identifier('date'),
        sql.Identifier('format'),
        sql.Identifier('url'))
    db_cursor.execute(tourny_id_query, (event_name, event_date, event_format, event_url))
    return int(db_cursor.fetchone()[0])


def update_tournament_info_size(tourny_id, size, db_cursor, logger):
    """
    Updates the size of the tournament with the given unique ID in the database associated with the given cursor.
    :param tourny_id: id of the event in the database
    :param size: new size to set of given tournament
    :param db_cursor: cursor of database where tournament info resides
    :param logger: logger to log info with
    :return: None"""
    update_query = sql.SQL('UPDATE {} SET {} = %s WHERE {} = %s').format(
        sql.Identifier('events', 'event_info'),
        sql.Identifier('size'),
        sql.Identifier('tourny_id'))
    db_cursor.execute(update_query, (size, tourny_id))
    logger.info(f'Updating size for tournament {tourny_id} to size {size}')


def insert_into_tournament_entry(tourny_id, deck_archetype, deck_placement, player_name, deck_name,
                                 placement_url, db_cursor, logger):
    """
    :param tourny_id:
    :param deck_archetype:
    :param deck_placement:
    :param player_name:
    :param deck_name:
    :param placement_url:
    :param db_cursor:
    :param logger:
    :return:"""

    def insert_query_func():
        insert_query = sql.SQL('INSERT INTO {} ({}, {}, {}, {}, {}, {}) VALUES (%s, %s, %s, %s, %s, %s)').format(
            sql.Identifier('events', 'event_entry'),
            sql.Identifier('tourny_id'),
            sql.Identifier('archetype'),
            sql.Identifier('place'),
            sql.Identifier('player'),
            sql.Identifier('deck_name'),
            sql.Identifier('url'))
        db_cursor.execute(insert_query, (tourny_id, deck_archetype, deck_placement, player_name, deck_name,
                                         placement_url))

    warning_msg = f'Duplicate entry for tournament_entry attempted, for key {tourny_id}, {deck_archetype}, ' \
                  f'{deck_placement}, {player_name}'
    su.execute_query_pass_on_unique_violation(insert_query_func, logger, warning_msg)


def get_tournament_entry_id(tourny_id, deck_archetype, deck_placement, player_name, db_cursor):
    """
    :param tourny_id:
    :param deck_archetype:
    :param deck_placement:
    :param player_name:
    :param db_cursor:
    :return:"""
    entry_id_query = sql.SQL('SELECT {} FROM {} WHERE {} = %s AND {} = %s AND {} = %s AND {} = %s').format(
        sql.Identifier('entry_id'),
        sql.Identifier('events', 'event_entry'),
        sql.Identifier('tourny_id'),
        sql.Identifier('archetype'),
        sql.Identifier('place'),
        sql.Identifier('player'))
    db_cursor.execute(entry_id_query, (tourny_id, deck_archetype, deck_placement, player_name))
    return int(db_cursor.fetchone()[0])


def insert_into_entry_card(entry_id, card_name, in_mainboard, quantity, db_cursor, logger):
    """
    :param entry_id:
    :param card_name:
    :param in_mainboard:
    :param quantity:
    :param db_cursor:
    :param logger:
    :return:"""

    def insert_query_func():
        insert_query = sql.SQL('INSERT INTO {} ({}, {}, {}, {}) VALUES (%s, %s, %s, %s)').format(
            sql.Identifier('events', 'entry_card'),
            sql.Identifier('entry_id'),
            sql.Identifier('card'),
            sql.Identifier('mainboard'),
            sql.Identifier('quantity'))
        db_cursor.execute(insert_query, (entry_id, card_name, in_mainboard, quantity))

    warning_msg = f'Duplicate entry for entry_card attempted: key {entry_id}, {card_name}, {in_mainboard}, {quantity}'
    su.execute_query_pass_on_unique_violation(insert_query_func, logger, warning_msg)
