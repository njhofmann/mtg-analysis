import pandas as pd
import analysis.utility as au
import datetime as dt
import pathlib as pl
import argparse as ap
from typing import List, Tuple

DEFAULT_DAY_LENGTH = 14


def create_pic_dirc(mtg_format: str, start_date: str, end_date: str) -> pl.Path:
    """Returns, and creates if needed, a series of directories to store search results under when searching under the
    given path - from start date to end date
    :param mtg_format: MTG format that was searched under
    :param start_date: date the search was started
    :param end_date: date the search was ended
    :return: Path containing the resulting directory
    """
    dirc = pl.Path(f'{mtg_format}/{start_date}_to_{end_date}')
    dirc.mkdir(parents=True, exist_ok=True)
    return dirc


def get_metagame_comp(date: str, length: int, mtg_format: str) -> List[Tuple[str, int]]:
    """Retrieves the metagame composition, at the archetype level, for the given format starting at 'date' - 'length'
    days until 'date'
    :param date: date at which query ends
    :param length: number of days before given date to start query
    :param mtg_format: MTG format to search under
    :return: list of archetype name and its metagame percentage
    """
    query = au.load_query('query.sql').format(date=date, length=length, format=mtg_format)
    return au.generic_search(query)


def metagame_comp_over_time(start_date: str, end_date: str, length: int, mtg_format: str) -> pd.DataFrame:
    """Returns a Dataframe containing metagame compositions from the given start date to end date, over rolling periods
    of 'length' days, for the given format. For each day between the start and end, returns the metagame makeup for that
    day and the past 'length' days. Each row in returned dataframe contains date, archetype, and percentage that
    archetype made up in metagame on that day
    :param start_date: dates to start from
    :param end_date: date to end at
    :param length: how many previous days to consider in metgame makeup for a given day
    :param mtg_format: format to search under
    :return: Dataframe with metagame compositions over time
    """
    dates_to_metagames = {date: get_metagame_comp(date, length, mtg_format)
                          for date in au.date_range(start_date, end_date, length)}
    rows = [(date, *metagame) for date, metagames in dates_to_metagames.items() for metagame in metagames]
    data_frame = pd.DataFrame(columns=['date', 'archetype', 'percentage'], data=rows)
    data_frame['date'] = pd.to_datetime(data_frame['date'])  # set as date type
    data_frame = data_frame.set_index(pd.DatetimeIndex(data_frame['date']))
    return data_frame


def parse_user_args() -> ap.Namespace:
    """Parses user entered arguments via 'sys.argv', throws errors on an invalid or missing required arguments.
    :return: Namespace listing out user entered args
    """

    def valid_date(date: str) -> str:
        try:
            return dt.datetime.strptime(date, '%Y-%M-%d').strftime('%Y-%M-%d')
        except ValueError as e:
            raise ValueError(f'date must be in form of "year-month-day"')

    parser = ap.ArgumentParser()
    parser.add_argument('-s', required=True, help='start date', type=valid_date)
    parser.add_argument('-e', required=True, help='end date', type=valid_date)
    parser.add_argument('-f', required=True, help='MTG format')
    parser.add_argument('-l', required=True, help='number of days to use as average for queried days')
    return parser.parse_args()  # user args by default
