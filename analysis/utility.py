import database.db_reader as ddr
import psycopg2
import numpy as np
import matplotlib.dates as mpd
import pathlib as pl
from typing import Union, List, Generator, Iterable
import datetime as dt
import pandas as pd

# universal matplotlib plot args
PLOT_ARGS = {'linestyle': '-', 'marker': ',', 'xdate': True}


def generic_search(search_query: str) -> List:
    """Generic function that executes a search query in the database and returns the results.
    :param search_query: search query to execute
    :return: results of search query
    """
    with psycopg2.connect(user=ddr.USER, database=ddr.DATABASE_NAME) as con:
        with con.cursor() as cursor:
            cursor.execute(search_query)
            return cursor.fetchall()


def load_query(path: Union[str, pl.Path]) -> str:
    """Loads the SQL query at the given path as a String
    :param path: path to the SQL file to load
    :return: SQL file as string
    """
    with open(path, 'r') as f:
        lines = f.readlines()
    return ''.join(lines)


def date_range(start: str, end: str, start_buffer: int) -> Generator[str, None, None]:
    """Generator giving the dates between the given start and end dates (inclusive), starting 'start_buffer' days after
    start date. Dates are in the form of "year-month-day"
    :param start: start date
    :param end: end date
    :param start_buffer: days after start date to begin generating
    :return: stream of dates between start and end date
    """
    date_format = '%Y-%m-%d'
    convert = lambda x: dt.datetime.strptime(x, date_format).date()
    start = convert(start) + dt.timedelta(days=start_buffer)
    end = convert(end) + dt.timedelta(days=1)
    for i in range((end - start).days):
        yield start.strftime(date_format)
        start += dt.timedelta(days=1)


def to_matplotlib_dates(dates: Iterable[str]) -> np.array:
    """Converts a series of String dates in the form of "year-month-day" into Matplotlib dates
    :param dates: series of String dates
    :return: converted series of dates
    """
    return np.array([mpd.datestr2num(date) for date in dates])


def fill_in_time(data_frame: pd.DataFrame, date_col: str, dependent_col: str) -> pd.DataFrame:
    """Give a DataFrame with a series of dates as its index (and its own identical date column) and a column that is
    dependent on the date, fills in all missing dates (such that the index is sequential by day) and interpolates the
    dependent column of all newly added rows
    :param data_frame: DataFrame to operate on
    :param date_col: name of date column matching the date index
    :param dependent_col: name of the column that is dependent on the date index / column
    :return: given DataFrame with missing dates "filled in"
    """
    data_frame = data_frame.resample('D').asfreq()
    data_frame[date_col] = data_frame.index
    data_frame[dependent_col] = data_frame[dependent_col].interpolate('time')
    return data_frame


if __name__ == '__main__':
    print([i for i in date_range('2019-01-13', '2020-07-23', 14)])
