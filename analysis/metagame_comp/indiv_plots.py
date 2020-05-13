import analysis.utility as au
import analysis.moving_average as ma
import analysis.metagame_comp.common as c

import datetime as dt
from typing import Tuple
import pathlib as pl
import sys

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import scipy.interpolate as spi
import scipy.stats as scs

"""Creates plots showing changes in metagame make up for every deck archetype appearing within a given time period for a 
given period"""

SPLINE_DEGREE = 2


def create_pic_dirc(format: str, start_date: str, end_date: str) -> pl.Path:
    """Returns, and creates if needed, a series of directories to store search results under when searching under the
    given path - from start date to end date
    :param format: MTG format that was searched under
    :param start_date: date the search was started
    :param end_date: date the search was ended
    :return: Path containing the resulting directory
    """
    dirc = pl.Path(f'{format}/{start_date}_to_{end_date}')
    dirc.mkdir(parents=True, exist_ok=True)
    return dirc


def spline_estimate(x: np.array, y: np.array) -> np.array:
    """Returns a single variable spline for the given x & y data, fitting a spline function to x & y - but then
    returning the spline estimate on x
    :param x: 1D array of x data
    :param y: 1D array of y data
    :return: spline estimate of x, from function fitted to x & y
    """
    return spi.UnivariateSpline(x=x, y=y, k=SPLINE_DEGREE)(x)


def linear_estimate(x: np.array, y: np.array) -> np.array:
    slope, intercept, _, _, _ = scs.linregress(x, y)
    return (slope * x) + intercept


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
        group = au.fill_in_time(group, 'date', 'percentage')

        fig, axes = plt.subplots()

        dates = au.to_matplotlib_dates(group['date'].astype(dtype=str))  # TODO fix me
        percents = group['percentage'].to_numpy(dtype=np.float)
        fitted_percents = spline_estimate(dates, percents)
        linear_fit = linear_estimate(dates, percents)

        # axes.plot_date(x=dates, y=percents, color='r', label='Raw Points', markersize=1)
        axes.plot_date(x=dates, y=percents, color='purple', label='Raw Line', **au.PLOT_ARGS)
        # axes.plot_date(x=dates, y=fitted_percents, color='g', label='Spline Estimate', **plot_args)
        axes.plot_date(x=dates, y=linear_fit, color='b', label='Linear Estimate', **au.PLOT_ARGS)
        # axes.plot_date(*ma.central_moving_average(dates, percents, side_size=20), color='g', label='Moving Avg', **plot_args)
        axes.plot_date(*ma.trailing_moving_avg(dates, percents, trail_size=30, method='u', recur=1), color='r',
                       label='Cum Avg', **au.PLOT_ARGS)
        axes.plot_date(*ma.trailing_moving_avg(dates, percents, trail_size=30, method='u', recur=2), color='green',
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
    data = c.metagame_comp_over_time(start_date, end_date, length, mtg_format)
    title_path = create_pic_dirc(mtg_format, start_date, end_date)

    if plot_type == 'i':
        plot_indiv_metagame_comps(data, title_path)


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
