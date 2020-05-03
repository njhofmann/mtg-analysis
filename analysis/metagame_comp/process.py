import analysis.utility as qu

import datetime as dt
from typing import Tuple, List, Iterable, Generator
import pathlib as pl
import sys

import matplotlib.dates as mpd
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import scipy.interpolate as spi
import scipy.stats as scs

"""Collection of queries for drawing together useful collections of data for analysis"""

SPLINE_DEGREE = 2
DEFAULT_DAY_LENGTH = 14  # 3 weeks


def get_metagame_comp(date: str, length: int, mtg_format: str) -> List[Tuple[str, int]]:
    """Retrieves the metagame composition, at the archetype level, for the given format starting at 'date' - 'length'
    days until 'date'
    :param date: date at which query ends
    :param length: number of days before given date to start query
    :param mtg_format: MTG format to search under
    :return: list of archetype name and its metagame percentage"""
    query = qu.load_query('query.sql').format(date=date, length=length, format=mtg_format)
    return qu.generic_search(query)


def metagame_comp_over_time(start_date: str, end_date: str, length: int, mtg_format: str) -> pd.DataFrame:
    """Returns a Dataframe containing metagame compositions from the given start date to end date, over rolling periods
    of 'length' days, for the given format. For each day between the start and end, returns the metagame makeup for that
    day and the past 'length' days. Each row in returned dataframe contains date, archetype, and percentage that
    archetype made up in metagame on that day
    :param start_date: dates to start from
    :param end_date: date to end at
    :param length: how many previous days to consider in metgame makeup for a given day
    :param mtg_format: format to search under
    :return: Dataframe with metagame compositions over time"""
    dates_to_metagames = {date: get_metagame_comp(date, length, mtg_format)
                          for date in qu.date_range(start_date, end_date, length)}
    rows = [(date, *metagame) for date, metagames in dates_to_metagames.items() for metagame in metagames]
    data_frame = pd.DataFrame(columns=['date', 'archetype', 'percentage'], data=rows)
    data_frame['date'] = pd.to_datetime(data_frame['date'])  # set as date type
    data_frame = data_frame.set_index(pd.DatetimeIndex(data_frame['date']))
    return data_frame


def create_pic_dirc(format: str, start_date: str, end_date: str) -> pl.Path:
    """Returns, and creates if needed, a series of directories to store search results under when searching under the
    given path - from start date to end date
    :param format: MTG format that was searched under
    :param start_date: date the search was started
    :param end_date: date the search was ended
    :return: Path containing the resulting directory"""
    dirc = pl.Path(f'{format}/{start_date}_to_{end_date}')
    dirc.mkdir(parents=True, exist_ok=True)
    return dirc


def spline_estimate(x: np.array, y: np.array) -> np.array:
    """Returns a single variable spline for the given x & y data, fitting a spline function to x & y - but then
    returning the spline estimate on x
    :param x: 1D array of x data
    :param y: 1D array of y data
    :return: spline estimate of x, from function fitted to x & y"""
    return spi.UnivariateSpline(x=x, y=y, k=SPLINE_DEGREE)(x)


def linear_estimate(x: np.array, y: np.array) -> np.array:
    slope, intercept, _, _, _ = scs.linregress(x, y)
    return (slope * x) + intercept


def to_matplotlib_dates(dates: Iterable[str]) -> np.array:
    """Converts a series of String dates in the form of "year-month-day" into Matplotlib dates
    :param dates: series of String dates
    :return: converted series of dates"""
    return np.array([mpd.datestr2num(date) for date in dates])


def plot_top_k() -> None:
    pass


def fill_in_time(group: pd.DataFrame) -> pd.DataFrame:
    group = group.resample('D').asfreq()
    group['date'] = group.index
    group['percentage'] = group['percentage'].interpolate('time')
    return group


def plot_indiv_metagame_comps(metagame_comps: pd.DataFrame, save_dirc: pl.Path) -> None:
    """For each archetype present in the given set of metagame data, plots the changes in that archetype's performance
    overtime on its own graph. Raw data and fitted line for approximation are function are listed on each plot. Graphs
    are saved under the given directory.
    :param metagame_comps:
    :param save_dirc:
    :return:
    """
    archetype_groups = metagame_comps.groupby('archetype')

    # to get consistent x and y axis across subplots
    all_dates = to_matplotlib_dates(metagame_comps['date'].astype(dtype=str).sort_values().unique())
    max_percentage = np.full(len(all_dates), fill_value=metagame_comps['percentage'].head(10).mean())

    plot_args = {'linestyle': '-', 'marker': ',', 'xdate': True}
    for archetype, group in archetype_groups:

        # interpolate missing dates
        group = group.sort_index()
        group = fill_in_time(group)

        fig, axes = plt.subplots()

        dates = to_matplotlib_dates(group['date'].astype(dtype=str))
        percents = group['percentage'].to_numpy(dtype=np.float)
        fitted_percents = spline_estimate(dates, percents)
        linear_fit = linear_estimate(dates, percents)

        axes.plot_date(x=dates, y=percents, color='r', label='Raw Points', markersize=1)
        axes.plot_date(x=dates, y=percents, color='purple', label='Raw Line', **plot_args)
        axes.plot_date(x=dates, y=fitted_percents, color='g', label='Spline Estimate', **plot_args)
        axes.plot_date(x=dates, y=linear_fit, color='b', label='Linear Estimate', **plot_args)
        axes.plot_date(x=all_dates, y=max_percentage, color='w', **plot_args)  # aligns x and y axis across all plots
        axes.legend()

        title = ' '.join([word.capitalize() for word in archetype.split(' ')])
        plt.title(title)
        plt.xlabel('Date')
        plt.ylabel('Metagame Percentage')
        plt.setp(axes.get_xticklabels(), rotation=30, horizontalalignment='right')
        plt.tight_layout()

        archetype = archetype.replace(' ', '_').replace('/', '\\')
        save_name = '_'.join([word.lower() for word in archetype.split(' ')])

        if save_name:
            save_path = save_dirc.joinpath(save_name)
            plt.savefig(save_path)

        plt.close(fig)


def main(start_date: str, end_date: str, mtg_format: str, length: int) -> None:
    data = metagame_comp_over_time(start_date, end_date, length, mtg_format)
    title_path = create_pic_dirc(mtg_format, start_date, end_date)
    plot_indiv_metagame_comps(data, title_path)


def parse_args() -> Tuple[str, str, str, int]:
    args = sys.argv

    def valid_date(date: str) -> str:
        try:
            return dt.datetime.strptime(date, '%Y-%M-%d').strftime('%Y-%M-%d')
        except ValueError as e:
            raise ValueError(f'date must be in form of "year-month-day"')

    if len(args) not in (4, 5):
        raise ValueError(f'usage {args[0]}: start-date, end-date, format, length (optional)')

    length = DEFAULT_DAY_LENGTH if len(args) == 4 else int(args[-1])
    return valid_date(args[1]), valid_date(args[2]), args[3], length


if __name__ == '__main__':
    main(*parse_args())
