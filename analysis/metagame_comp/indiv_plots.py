import analysis.utility as au
import analysis.moving_average as ma

import datetime as dt
from typing import Tuple, List, Iterable
import pathlib as pl
import re
import sys

import matplotlib.dates as mpd
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import scipy.interpolate as spi
import scipy.stats as scs

"""Collection of queries for drawing together useful collections of data for analysis"""

SPLINE_DEGREE = 2
DEFAULT_DAY_LENGTH = 14


def get_metagame_comp(date: str, length: int, mtg_format: str) -> List[Tuple[str, int]]:
    """Retrieves the metagame composition, at the archetype level, for the given format starting at 'date' - 'length'
    days until 'date'
    :param date: date at which query ends
    :param length: number of days before given date to start query
    :param mtg_format: MTG format to search under
    :return: list of archetype name and its metagame percentage"""
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
    :return: Dataframe with metagame compositions over time"""
    dates_to_metagames = {date: get_metagame_comp(date, length, mtg_format)
                          for date in au.date_range(start_date, end_date, length)}
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


def select_top_decks(metagame_comps: pd.DataFrame) -> List[Tuple[str, float]]:
    # TODO figure out proper selection criteria
    row_count = len(metagame_comps)

    def ranking(group: pd.DataFrame) -> float:
        return sum(group['percentage']) / len(group)

    sorted_decks = sorted([(name, ranking(group)) for name, group in metagame_comps.groupby('archetype')],
                  key=lambda x: x[1], reverse=True)
    return list(map(lambda x: x[0], sorted_decks))[:10]


def create_other_data(other_decks: pd.DataFrame) -> pd.DataFrame:
    # fill out each group, recombine, group and average, recreate dataframe
    filled_groups = [fill_in_time(group) for name, group in other_decks.groupby('archetype')]
    filled_data_frame = pd.DataFrame(filled_groups)


def plot_metagame(metagame_comps: pd.DataFrame, save_dirc: pl.Path) -> None:
    major_deck_names = select_top_decks(metagame_comps)
    major_decks = metagame_comps[metagame_comps['archetype'].isin(major_deck_names)]
    other_decks = metagame_comps[~metagame_comps['archetype'].isin(major_deck_names)]

    for name, group in major_decks.groupby('archetype'):
        group = fill_in_time(group)
        group['date'] = group['date'].apply(mpd.date2num)
        avg = ma.trailing_moving_avg(group['date'], group['percentage'], trailing_size=45)
        plt.plot_date(*avg, label=name, **au.PLOT_ARGS)

    plt.title('Metagame Composition')
    plt.ylabel('Metagame Percentage')
    plt.xlabel('Date')
    plt.legend()
    plt.show()
    # plt.savefig(save_dirc)


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
    all_dates = au.to_matplotlib_dates(metagame_comps['date'].astype(dtype=str).sort_values().unique())
    max_percentage = np.full(len(all_dates), fill_value=metagame_comps['percentage'].head(10).mean())

    for archetype, group in archetype_groups:

        # interpolate missing dates
        group = group.sort_index()
        group = fill_in_time(group)

        fig, axes = plt.subplots()

        dates = au.to_matplotlib_dates(group['date'].astype(dtype=str))  # TODO fix me
        percents = group['percentage'].to_numpy(dtype=np.float)
        fitted_percents = spline_estimate(dates, percents)
        linear_fit = linear_estimate(dates, percents)

        #axes.plot_date(x=dates, y=percents, color='r', label='Raw Points', markersize=1)
        axes.plot_date(x=dates, y=percents, color='purple', label='Raw Line', **au.PLOT_ARGS)
        #axes.plot_date(x=dates, y=fitted_percents, color='g', label='Spline Estimate', **plot_args)
        axes.plot_date(x=dates, y=linear_fit, color='b', label='Linear Estimate', **au.PLOT_ARGS)
        #axes.plot_date(*ma.central_moving_average(dates, percents, side_size=20), color='g', label='Moving Avg', **plot_args)
        axes.plot_date(*ma.trailing_moving_avg(dates, percents, trailing_size=30, method='u', recur=1), color='r',
                       label='Cum Avg', **au.PLOT_ARGS)
        axes.plot_date(*ma.trailing_moving_avg(dates, percents, trailing_size=30, method='u', recur=2), color='green',
                       label='Cum Avg', **au.PLOT_ARGS)
        axes.plot_date(x=all_dates, y=max_percentage, color='w', **au.PLOT_ARGS)  # aligns x and y axis across all plots
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


def main(start_date: str, end_date: str, mtg_format: str, plot_type: str, length: int) -> None:
    data = metagame_comp_over_time(start_date, end_date, length, mtg_format)
    title_path = create_pic_dirc(mtg_format, start_date, end_date)

    if plot_type == 'i':
        plot_indiv_metagame_comps(data, title_path)
    elif plot_type == 'm':
        plot_metagame(data, title_path)


def parse_args() -> Tuple[str, str, str, str, int]:
    args = sys.argv

    def valid_date(date: str) -> str:
        try:
            return dt.datetime.strptime(date, '%Y-%M-%d').strftime('%Y-%M-%d')
        except ValueError as e:
            raise ValueError(f'date must be in form of "year-month-day"')

    if len(args) not in (5, 6):
        raise ValueError(f'usage {args[0]}: start-date, end-date, format, plot-type length (optional)')

    length = DEFAULT_DAY_LENGTH if len(args) == 5 else int(args[-1])
    plot_type = args[-1] if len(args) == 5 else args[-2]

    if plot_type not in ('i', 'm'):
        raise ValueError(f'valid plot types: i for individual plots, m for metagame plot')

    return valid_date(args[1]), valid_date(args[2]), args[3], plot_type, length


if __name__ == '__main__':
    main(*parse_args())
