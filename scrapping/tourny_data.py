"""Module for pulling tournament data from mtgtop8.com  """
import requests
import bs4
import re
import psycopg2
from psycopg2 import sql
import random
import time
import datetime
import logging
import psycopg2.errors

# psycopg2 constants
PSYCOPG2_UNIQUE_VIOLATION_CODE = 23505

# regex constants
EVENT_URL_REGEX = re.compile('event\?e=[0-9]+&f=[A-Z]+')
EVENT_SIZE_REGEX = re.compile('[0-9]+ players')
DECK_URL_REGEX = re.compile('\?e=[0-9]+&d=[0-9]+&f=[A-Z]+')
DECK_ARCHETYPE_REGEX = re.compile('archetype?\?a=[0-9]+')


def init_logging():
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)

    def init_channel(channel):
        formatter = logging.Formatter('%(asctime)s: %(message)s')
        channel.setFormatter(formatter)
        logger.addHandler(channel)
    init_channel(logging.StreamHandler())
    init_channel(logging.FileHandler('mtgtop8_scrapper.log', mode='w'))
    return logger


def get_and_wait(url, data=None):
    """
    Retrieves the data from the given search_url and returns a BeautifulSoup parser on the HTML the search_url response returns. Puts
    the thread to sleep for a random amount of seconds after retrieval to ensure that server being requested from isn't
    overwhelmed and that scrapping looks less conspicuous.
    :param url: search_url to fetch data from
    :param data: data to send with search_url, if desired
    :return: HTML BeautifulSoup parser on the HTML text the request on search_url returns
    """
    if data:
        url_data = requests.post(url=url, data=data)
    else:
        url_data = requests.get(url=url)
    time.sleep(random.randint(2, 7))
    return bs4.BeautifulSoup(markup=url_data.text, features='html.parser')


def format_date(date):
    """
    Formats a 'dd/mm/yyyy' date into a 'mm/dd/yyyy'.
    :param date:
    :return:
    """
    parsed_date = datetime.datetime.strptime(date, '%d/%m/%y')
    return parsed_date.strftime('%m/%d/%Y')


def get_size(event):
    possible_texts = event.find_all(class_='S14')
    for text in possible_texts:
        size = EVENT_SIZE_REGEX.match(text.get_text())
        if size:  # is not None
            return int(size.group())
    return None



def get_entry_rank(parent_elements):
    rank = parent_elements.find(class_='W14')
    if rank is None:
        rank = parent_elements.find(class_='S14')
    return rank.get_text()


def card_in_mainboard(card):
    """

    :param card:
    :return:
    """
    for prev_sib in card.parent.previous_siblings:
        has_class = prev_sib.find(class_='O13')
        if has_class is not None:
            title = has_class.get_text().lower()
            if 'sideboard' in title:
                return False
    return True


def insert_into_tournament_info(event_name, event_date, event_format, size, event_url, db_cursor, logger):
    def insert_query_func():
        insert_query = sql.SQL('INSERT INTO {} ({}, {}, {}, {}, {}) VALUES (%s, %s, %s, %s, %s)').format(
            sql.Identifier('tournament_info'), sql.Identifier('name'), sql.Identifier('date'), sql.Identifier('format'),
            sql.Identifier('size'), sql.Identifier('url'))
        db_cursor.execute(insert_query, (event_name, event_date, event_format, size, event_url))

    warning_msg = 'Duplicate entry for tournament_info attempted, key {}, {}'.format(event_name, event_date)
    execute_query_pass_on_unique_violation(insert_query_func, logger, warning_msg)


def get_tournament_info_id(event_name, event_date, event_format, event_url, db_cursor):
    tourny_id_query = sql.SQL('SELECT {} FROM {} WHERE {} = %s AND {} = %s AND {} = %s AND {} = %s').format(
        sql.Identifier('tourny_id'), sql.Identifier('tournament_info'), sql.Identifier('name'), sql.Identifier('date'),
        sql.Identifier('format'), sql.Identifier('url'))
    print(tourny_id_query, (event_name, event_date, event_format, event_url))
    db_cursor.execute(tourny_id_query, (event_name, event_date, event_format, event_url))
    print(tourny_id_query)
    return int(db_cursor.fetchone()[0])


def insert_into_tournament_entry(tourny_id, deck_archetype, deck_placement, player_name, deck_name,
                                 placement_url, db_cursor, logger):
    def insert_query_func():
        insert_query = sql.SQL(
            'INSERT INTO {} ({}, {}, {}, {}, {}, {}) VALUES (%s, %s, %s, %s, %s, %s)').format(
            sql.Identifier('tournament_entry'), sql.Identifier('tourny_id'), sql.Identifier('archetype'),
            sql.Identifier('place'), sql.Identifier('player'), sql.Identifier('deck_name'), sql.Identifier('url'))
        db_cursor.execute(insert_query, (tourny_id, deck_archetype, deck_placement, player_name, deck_name,
                                         placement_url))

    warning_msg = 'Duplicate entry for tournament_entry attempted, for key ' \
                  '{}, {}, {}, {}'.format(tourny_id, deck_archetype, deck_placement, player_name)
    execute_query_pass_on_unique_violation(insert_query_func, logger, warning_msg)


def get_tournament_entry_id(tourny_id, deck_archetype, deck_placement, player_name, db_cursor):
    entry_id_query = sql.SQL('SELECT {} FROM {} WHERE {} = %s AND {} = %s AND {} = %s AND {} = %s').format(
        sql.Identifier('entry_id'), sql.Identifier('tournament_entry'), sql.Identifier('tourny_id'),
        sql.Identifier('archetype'), sql.Identifier('place'), sql.Identifier('player'))
    db_cursor.execute(entry_id_query, (tourny_id, deck_archetype, deck_placement, player_name))
    return int(db_cursor.fetchone()[0])


def insert_into_entry_card(entry_id, card_name, in_mainboard, quantity, db_cursor, logger):
    def insert_query_func():
        insert_query = sql.SQL('INSERT INTO {} ({}, {}, {}, {}) VALUES (%s, %s, %s, %s)').format(
            sql.Identifier('entry_card'), sql.Identifier('entry_id'), sql.Identifier('card'),
            sql.Identifier('mainboard'), sql.Identifier('quantity'))
        db_cursor.execute(insert_query, (entry_id, card_name, in_mainboard, quantity))

    warning_msg = 'Duplicate entry for entry_card attempted, key {}, {}, {}, {}'.format(entry_id, card_name,
                                                                                        in_mainboard, quantity)
    execute_query_pass_on_unique_violation(insert_query_func, logger, warning_msg)


def execute_query_pass_on_unique_violation(query_func, logger, warning_msg):
    try:
        query_func()
    except psycopg2.IntegrityError as e:
        if e.pgcode != PSYCOPG2_UNIQUE_VIOLATION_CODE:
            logger.warning(warning_msg)
        else:
            raise e


def retrieve_and_parse(search_url, url_format, database, user='postgres'):
    """
    Given a url to a url_format webpage on mtgtop8.com, pulls all tournaments and their related placement info and loads
    them into the given Postgres database. Pulls all tournament info, placements in each tournament, cards played in
    each placement, etc.
    :param search_url:
    :param url_format: format being queried
    :param database: name of Postgres database
    :param user: login username for given database
    :return: None
    """
    logger = init_logging()
    base_url = re.match('.*.com/', search_url).group()
    page = 1
    min_event_count = 5
    with psycopg2.connect(user=user, dbname=database) as con:
        con.autocommit = True
        with con.cursor() as cursor:
            while True:
                child_page_value = {'cp': page}  # set page value
                soup = get_and_wait(search_url, child_page_value)
                parents = soup.find_all(class_='hover_tr')  # combine parent.find() into lambda
                events = [parent for parent in parents if parent.find(href=EVENT_URL_REGEX)]

                # parse out events in last major events column
                normal_events = []
                for parent in events:
                    if parent.previous_siblings is None:  # should never occur
                        normal_events.append(parent)
                    else:
                        major_event_header = any(['class="w_title"' in str(sibling)
                                                  and 'Last major events' in str(sibling)
                                                  for sibling in parent.previous_siblings])
                        if not major_event_header:
                            normal_events.append(parent)

                # empty pages means final page has been reached
                if len(events) < min_event_count:
                    break

                for event in normal_events:
                    logger.info('Fetching for page {}'.format(page))
                    page += 1

                    event_info = event.find(href=EVENT_URL_REGEX)
                    event_url = base_url + event_info['href']
                    event_name = event_info.get_text()
                    logger.info('Fetching event {} from {}'.format(event_name, event_url))
                    size = get_size(event)
                    event_date = format_date(event.find(class_='S10').get_text())
                    insert_into_tournament_info(event_name, event_date, url_format, size, event_url, cursor, logger)
                    tourny_id = get_tournament_info_id(event_name, event_date, url_format, event_url, cursor)
                    parse_event(tourny_id, event_name, event_date, event_url, base_url, cursor, logger)


def parse_event(tourny_id, event_name, event_date, event_url, base_url, db_cursor, logger):
    """
    Given the search_url of a tournament on mtgtop8.com, pulls all decks that placed in the tournament and enters them into
    the database of the given database cursor. Pulls player of each placement, the info of the deck they played, etc.
    :param event_name:
    :param event_date:
    :param event_url:
    :param base_url:
    :param db_cursor:
    :param logger:
    :return:
    """
    soup = get_and_wait(event_url)
    possible_parents = soup.find_all(class_=lambda tag: tag in ('chosen_tr', 'hover_tr'))
    deck_parents = [parent for parent in possible_parents if parent.find(href=DECK_URL_REGEX)]

    for parent in deck_parents:
        child_deck_tag = parent.find(href=DECK_URL_REGEX)
        deck_url = base_url + 'event' + child_deck_tag['href']
        deck_name = child_deck_tag.get_text()
        logger.info('Fetching tournament entry {} from {}'.format(deck_name, deck_url))
        deck_rank = get_entry_rank(parent)
        player_name = parent.find(class_='G11').get_text()
        parse_entry(tourny_id, deck_url, deck_name, deck_rank, player_name, db_cursor, logger)


def parse_entry(tourny_id, placement_url, deck_name, deck_placement, player_name, db_cursor, logger):
    """
    Given the search_url to a tournament placement on mtgtop8.com, pull the ranked deck's info in the database of the given
    database cursor. Info such as played cards, card quantities, player name, ranking, etc.
    :param event_name:
    :param placement_url:
    :param deck_name:
    :param deck_placement:
    :param db_cursor:
    :return: None
    """
    url_data = get_and_wait(placement_url)

    deck_archetype = url_data.find(href=DECK_ARCHETYPE_REGEX)
    if deck_archetype is None:
        deck_archetype = deck_name
    else:
        deck_archetype = deck_archetype.get_text()

    insert_into_tournament_entry(tourny_id, deck_archetype, deck_placement, player_name, deck_name, placement_url,
                                 db_cursor, logger)

    entry_id = get_tournament_entry_id(tourny_id, deck_archetype, deck_placement, player_name, db_cursor)

    cards = url_data.find_all(class_='G14')
    for card in cards:
        # check if in sideboard
        card_name = card.find(class_='L14').get_text()
        logger.info('Fetching card {} from {}'.format(card_name, placement_url))
        in_mainboard = str(card_in_mainboard(card))
        quantity = int(card.find(class_='hover_tr').get_text().split(' ')[0])  # TODO clean up
        insert_into_entry_card(entry_id, card_name, in_mainboard, quantity, db_cursor, logger)


if __name__ == '__main__':
    urls_and_formats = [('https://www.mtgtop8.com/format?f=MO&meta=44', 'modern'),
                        ('https://www.mtgtop8.com/format?f=LE&meta=16', 'legacy'),
                        ('https://www.mtgtop8.com/format?f=ST&meta=58', 'standard')]
    for url, url_format in urls_and_formats:
        retrieve_and_parse(url, url_format, 'mtg_analysis')
