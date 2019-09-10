"""Module for pulling tournament data from mtgtop8.com  """
import requests
import bs4
import re
import psycopg2
from psycopg2 import sql
import random
import time

# regex constants
EVENT_URL_REGEX = re.compile('event\?e=[0-9]+&f=[A-Z]+')
DECK_URL_REGEX = re.compile('\?e=[0-9]+&d=[0-9]+&f=[A-Z]+')


def get_and_wait(url, data=None):
    """
    Retrieves the data from the given url and returns a BeautifulSoup parser on the HTML the url response returns. Puts
    the thread to sleep for a random amount of seconds after retrieval to ensure that server being requested from isn't
    overwhelmed and that scrapping looks less conspicuous.
    :param url: url to fetch data from
    :param data: data to send with url, if desired
    :return: HTML BeautifulSoup parser on the HTML text the request on url returns
    """
    if data:
        url_data = requests.post(url=url, data=data)
    else:
        url_data = requests.get(url=url)
    time.sleep(random.randint(2, 7))
    return bs4.BeautifulSoup(markup=url_data.text, features='html.parser')


def retrieve_and_parse(url, format, database, user='postgres'):
    """
    Given a url to a format webpage on mtgtop8.com, pulls all tournaments and their related placement info and loads
    them into the given Postgres database. Pulls all tournament info, placements in each tournament, cards played in
    each placement, etc.
    :param url:
    :param format: format being queried
    :param database: name of Postgres database
    :param user: login username for given database
    :return: None
    """
    base_url = re.match('.*.com/', url)
    page = 1
    min_event_count = 5
    with psycopg2.connect(user=user, dbname=database) as con:
        con.autocommit = True
        with con.cursor() as cursor:
            while True:
                child_page_value = {'cp': page}  # set page value
                soup = get_and_wait(url, child_page_value)
                parents = soup.find_all(class_='hover_tr')  # combine parent.find() into lambda
                events = [parent for parent in parents if parent.find(href=EVENT_URL_REGEX)]

                # empty pages means final page has been reached
                if len(events) < min_event_count:
                    break

                for event in events:
                    event_info = event.find(href=EVENT_URL_REGEX)
                    event_url = base_url + event_info['href']
                    event_name = event_info.get_text()
                    event_date = event.find(class_='S10').get_text()
                    insert_query = sql.SQL('INSERT INTO {} ({}, {}, {}, {}) VALUES (%s, %s, %s, %s)').format(
                        sql.Identifier('TournamentInfo'), sql.Identifier('name'), sql.Identifier('format'),
                        sql.Identifier('date'), sql.Identifier('date'))
                    cursor.execute(insert_query, (event_name, format, event_date, event_url))
                    parse_event(event_name, event_url, cursor)
                    page += 1


def parse_event(event_name, event_url, base_url, db_cursor):
    """
    Given the url of a tournament on mtgtop8.com, pulls all decks that placed in the tournament and enters them into
    the database of the given database cursor. Pulls player of each placement, the info of the deck they played, etc.
    :param event_name:
    :param event_url:
    :param base_url:
    :param db_cursor:
    :return:
    """
    soup = get_and_wait(event_url)
    possible_parents = soup.find_all(lambda tag: tag.class_ in ('chosen_tr', 'hover_tr'))
    deck_parents = [parent for parent in possible_parents if parent.find(href=DECK_URL_REGEX)]

    for parent in deck_parents:
        child_deck_tag = deck_parents.find(href=DECK_URL_REGEX)
        deck_url = base_url + 'event' + child_deck_tag['href']
        deck_name = child_deck_tag.get_text()
        deck_rank = parent.find(class_='S14').get_text()
        parse_event(event_name, deck_url, deck_name, deck_rank, db_cursor)


def parse_entry(event_name, placement_url, deck_name, deck_placement, db_cursor):
    """
    Given the url to a tournament placement on mtgtop8.com, pull the ranked deck's info in the database of the given
    database cursor. Info such as played cards, card quantities, player name, ranking, etc.
    :param event_name:
    :param placement_url:
    :param deck_name:
    :param deck_placement:
    :param db_cursor:
    :return:
    """
    pass



if __name__ == '__main__':
    url = 'https://www.mtgtop8.com/format?f=MO&meta=44'
    format = 'modern'
    retrieve_and_parse(url, format, 'mtg_analysis')