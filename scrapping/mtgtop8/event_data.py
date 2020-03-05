import re
import random
import time
import psycopg2.errors
import scrapping.mtgtop8.db_conns as dbc
import scrapping.mtgtop8.parsing as prs
import requests
import bs4
from scrapping.utility import init_logging
import database.db_reader as dbr

"""Module for pulling tournament data from mtgtop8.com."""


def get_and_wait(url, data=None):
    """Retrieves the data from the given url and returns a BeautifulSoup parser on the HTML the url response returns. Puts
    the thread to sleep for a random amount of seconds after retrieval to ensure that server being requested from isn't
    overwhelmed and that scrapping appears less conspicuous.
    :param url: url to fetch data from
    :param data: any additional data to send with url_data, treats as a post request if included
    :return: HTML BeautifulSoup parser on the HTML text the request on url_data returns"""
    url_data = requests.post(url=url, data=data) if data else requests.get(url=url)
    time.sleep(random.random() * 2)
    return bs4.BeautifulSoup(markup=url_data.text, features='html.parser')


def retrieve_and_parse(search_url, url_format, page, database, logger, prod_mode, user=dbr.USER):
    """Given a search to a format's webpage on mtgtop8.com, pulls all tournaments and their related placement info and
    loads them into the given Postgres database. Pulls all tournament info, placements in each tournament, cards played
    in each entry, etc.
    :param search_url: main url page to parse
    :param url_format: format being queried
    :param database: name of Postgres database
    :param logger: logger to use for logging info
    :param user: login user for given database
    :return: None"""
    with psycopg2.connect(user=user, dbname=database) as con:
        con.autocommit = True
        with con.cursor() as cursor:
            parsing = True
            while parsing:
                base_url = re.match('.*.com/', search_url).group()
                logger.info(f'Fetching for page {page} in format {url_format} from url {search_url}')
                child_page_value = {'cp': page}  # set page value
                url_soup = get_and_wait(search_url, child_page_value)
                events = prs.get_events_from_page(url_soup, base_url, logger)

                if events:
                    for event_name, event_date, event_url in events:
                        dbc.insert_into_tournament_info(event_name, event_date, url_format, event_url, cursor, logger, prod_mode)
                        tourny_id = dbc.get_tournament_info_id(event_name, event_date, url_format, event_url, cursor)
                        parse_event(tourny_id, event_url, base_url, cursor, logger, prod_mode)
                    page += 1
                else:
                    parsing = False


def parse_event(tourny_id, event_url, base_url, db_cursor, logger, prod_mode):
    """Given the url_data of a tournament on mtgtop8.com, pulls all decks that placed in the tournament and enters them into
    into the database of the given database cursor. Pulls player of each placement, the info of the deck they played,
    etc.
    :param tourny_id: if of event to parse
    :param event_url: url of the event to parse
    :param base_url: base url to combine with parsed deck entry urls
    :param db_cursor: cursor of the database to insert info in
    :param logger: logger to log info with
    :param prod_mode:
    :return: None"""
    url_data = get_and_wait(event_url)
    deck_parents, event_size = prs.get_event_info(url_data)

    if event_size:
        dbc.update_tournament_info_size(tourny_id, event_size, db_cursor, logger)

    for parent in deck_parents:
        entry_url_ending, deck_name, deck_rank, player_name = prs.get_event_entry_info(parent)
        entry_url = base_url + entry_url_ending
        logger.info('Fetching tournament entry {} from {}'.format(deck_name, entry_url))
        parse_entry(tourny_id, entry_url, deck_name, deck_rank, player_name, db_cursor, logger, prod_mode)


def parse_entry(tourny_id, placement_url, deck_name, deck_placement, player_name, db_cursor, logger, prod_mode):
    """Given the url to a deck placement for a tournament on mtgtop8.com, pull the ranked deck's info in the database of
    the given database cursor. Info such as played cards, card quantities, player name, ranking, etc.
    :param tourny_id: id of the tournament the deck was entered in
    :param placement_url: url containing ranked deck info
    :param deck_name: name of the deck
    :param deck_placement: rank of the deck in the associated tournament
    :param player_name: name of deck's pilot
    :param db_cursor: cursor of database info will be entered into
    :param logger: logger to log status of scrapping
    :param prod_mode:
    :return: None"""
    url_soup = get_and_wait(placement_url)

    # deck archetype can only be retrieved from deck url
    cards, deck_archetype = prs.get_entry_deck_info(url_soup)

    if deck_archetype is None:
        deck_archetype = deck_name

    # insert deck specific info (ie not card info)
    dbc.insert_into_tournament_entry(tourny_id, deck_archetype, deck_placement, player_name, deck_name, placement_url,
                                     db_cursor, logger, prod_mode)

    # get unique id for entered deck, to use for entering
    entry_id = dbc.get_tournament_entry_id(tourny_id, deck_archetype, deck_placement, player_name, db_cursor)

    # insert every card in deck
    for card in cards:
        card_name, in_mainboard, quantity = prs.get_card_info(card)
        logger.info(f'Fetching card {card_name} from {entry_id}')
        dbc.insert_into_entry_card(entry_id, card_name, in_mainboard, quantity, db_cursor, logger, prod_mode)


def main(prod_mode):
    #('https://www.mtgtop8.com/format?f=MO&meta=44', 'modern', 0),
    urls_and_formats = [
                        ('https://www.mtgtop8.com/format?f=LE&meta=16', 'legacy', 0),
                        ('https://www.mtgtop8.com/format?f=ST&meta=58', 'standard', 1),
                        ('https://www.mtgtop8.com/format?f=PI&meta=191', 'pioneer', 1)]
    logger = init_logging('mtgtop8_scrapper.log')
    for url, url_format, page in urls_and_formats:
        try:
            retrieve_and_parse(url, url_format, page, dbr.DATABASE_NAME, logger, prod_mode)
        except Exception as e:
            if prod_mode:
                logger.warning(str(e))
            else:
                raise e


if __name__ == '__main__':
    main(False)
