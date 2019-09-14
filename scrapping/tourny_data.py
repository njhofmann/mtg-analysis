"""Module for pulling tournament data from mtgtop8.com  """
import requests
import bs4
import re
import psycopg2
from psycopg2 import sql
import random
import time
import datetime

# regex constants
EVENT_URL_REGEX = re.compile('event\?e=[0-9]+&f=[A-Z]+')
DECK_URL_REGEX = re.compile('\?e=[0-9]+&d=[0-9]+&f=[A-Z]+')
DECK_ARCHETYPE_REGEX = re.compile('archetype?\?a=[0-9]+')


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


def format_date(date):
    """
    Formats a 'dd/mm/yyyy' date into a 'mm/dd/yyyy'.
    :param date:
    :return:
    """
    parsed_date = datetime.datetime.strptime(date, '%d/%m/%y')
    return parsed_date.strftime('%m/%d/%Y')

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
    base_url = re.match('.*.com/', url).group()
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

                normal_events = []  # parse out events in last major events column
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
                    event_info = event.find(href=EVENT_URL_REGEX)
                    event_url = base_url + event_info['href']
                    event_name = event_info.get_text()
                    event_date = format_date(event.find(class_='S10').get_text())
                    insert_query = sql.SQL('INSERT INTO {} ({}, {}, {}, {}) VALUES (%s, %s, %s, %s)').format(
                        sql.Identifier('tournament_info'), sql.Identifier('name'), sql.Identifier('date'),
                        sql.Identifier('format'), sql.Identifier('url'))
                    cursor.execute(insert_query, (event_name, event_date, format, event_url))
                    parse_event(event_name, event_date, event_url, base_url, cursor)
                    page += 1


def parse_event(event_name, event_date, event_url, base_url, db_cursor):
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
    possible_parents = soup.find_all(class_=lambda tag: tag in ('chosen_tr', 'hover_tr'))
    deck_parents = [parent for parent in possible_parents if parent.find(href=DECK_URL_REGEX)]

    for parent in deck_parents:
        child_deck_tag = parent.find(href=DECK_URL_REGEX)
        deck_url = base_url + 'event' + child_deck_tag['href']
        deck_name = child_deck_tag.get_text()
        deck_rank = parent.find(class_='W14').get_text()
        player_name = parent.find(class_='G11').get_text()
        parse_entry(event_name, event_date, deck_url, deck_name, deck_rank, player_name, db_cursor)


def parse_entry(event_name, event_date, placement_url, deck_name, deck_placement, player_name, db_cursor):
    """
    Given the url to a tournament placement on mtgtop8.com, pull the ranked deck's info in the database of the given
    database cursor. Info such as played cards, card quantities, player name, ranking, etc.
    :param event_name:
    :param placement_url:
    :param deck_name:
    :param deck_placement:
    :param db_cursor:
    :return: None
    """
    url_data = get_and_wait(placement_url)
    deck_archetype = url_data.find(href=DECK_ARCHETYPE_REGEX).get_text()

    insert_query = sql.SQL('INSERT INTO {} ({}, {}, {}, {}, {}, {}, {}) VALUES (%s, %s, %s, %s, %s, %s, %s)').format(
        sql.Identifier('tournament_entry'), sql.Identifier('tournament'), sql.Identifier('date'),
        sql.Identifier('archetype'), sql.Identifier('place'), sql.Identifier('player'), sql.Identifier('name'),
        sql.Identifier('url'))
    db_cursor.execute(insert_query, (event_name, event_date, deck_archetype, deck_placement, player_name, deck_name,
                                     placement_url))

    # get created entry id for previously entered entry
    entry_id_query = sql.SQL('SELECT {} FROM {} WHERE {} = %s AND {} = %s AND {} = %s AND {} = %s AND {} = %s').format(
        sql.Identifier('entry_id'), sql.Identifier('tournament_entry'), sql.Identifier('tournament'),
        sql.Identifier('date'), sql.Identifier('archetype'), sql.Identifier('place'), sql.Identifier('player')
    )
    db_cursor.execute(entry_id_query, (event_name, event_date, deck_archetype, deck_placement, player_name))
    entry_id = int(db_cursor.fetchone()[0])

    cards = url_data.find_all(class_='G14')
    for card in cards:
        # check if in sideboard
        in_mainboard = is_in_mainboard(card)
        quantity = int(card.find(class_='hover_tr').get_text().split(' ')[0])  # TODO clean up
        card_name = card.find(class_='L14').get_text()
        insert_query = sql.SQL('INSERT INTO {} ({}, {}, {}, {}) VALUES (%s, %s, %s, %s)').format(
            sql.Identifier('entry_card'), sql.Identifier('entry_id'), sql.Identifier('card'),
            sql.Identifier('mainboard'), sql.Identifier('quantity'))
        db_cursor.execute(insert_query,
                          (entry_id, card_name, str(in_mainboard), quantity))


def is_in_mainboard(card):
    """

    :param card:
    :return:
    """
    for prev_sib in card.previous_siblings:
        has_class = prev_sib.find(class_='O13')
        if has_class is not None:
            title = has_class.get_text().lower()
            if 'sideboard' in title:
                return False
    return True


if __name__ == '__main__':
    url = 'https://www.mtgtop8.com/format?f=MO&meta=44'
    format = 'modern'
    retrieve_and_parse(url, format, 'mtg_analysis')
