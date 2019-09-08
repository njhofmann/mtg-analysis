"""Module for pulling tournament data from mtgtop8.com  """
import requests
import bs4
import re
import psycopg2
from psycopg2 import sql


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
            event_regex = re.compile('event\?e=[0-9]+&f=MO')
            while True:
                child_page_value = {'cp': page}  # set page value
                url_data = requests.post(url, data=child_page_value)
                soup = bs4.BeautifulSoup(markup=url_data.text, features='html.parser')
                parents = soup.find_all(class_='hover_tr')
                events = [parent for parent in parents if parent.find(href=event_regex)]

                # empty pages means final page has been reached
                if len(events) < min_event_count:
                    break

                for event in events:
                    event_info = event.find(href=event_regex)
                    event_url = base_url + event_info['href']
                    event_name = event_info.get_text()
                    event_date = event.find(class_='S10').get_text()
                    insert_query = sql.SQL('INSERT INTO {} ({}, {}, {}, {}) VALUES (%s, %s, %s, %s)').format(
                        sql.Identifier('TournamentInfo'), sql.Identifier('name'), sql.Identifier('format'),
                        sql.Identifier('date'), sql.Identifier('date'))
                    cursor.execute(insert_query, (event_name, format, event_date, event_url))
                    parse_event(event_name, event_url, cursor)
                    page += 1


def parse_event(event_name, event_url, db_cursor):
    """
    Given the url of a tournament on mtgtop8.com, pulls all decks that placed in the tournament and enters them into
    the database of the given database cursor. Pulls player of each placement, the info of the deck they played, etc.
    :param event_name: name of the tournament
    :param event_url: url to tournament placements
    :param db_cursor: cursor to load pulled info into
    :return: None
    """
    pass


def parse_entry(event_name, placement_url, db_cursor):
    """
    Given the url to a tournament placement on mtgtop8.com, pull the ranked deck's info in the database of the given
    database cursor. Info such as played cards, card quantities, player name, ranking, etc.
    :param event_name:
    :param placement_url:
    :param db_cursor:
    :return:
    """
    pass



if __name__ == '__main__':
    url = 'https://www.mtgtop8.com/format?f=MO&meta=44'
    format = 'modern'
    retrieve_and_parse(url, format, 'mtg_analysis')