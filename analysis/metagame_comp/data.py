import analysis.utility as qu
import pandas as pd
import argparse as ap
import scipy.interpolate as spi
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.dates as mpd
from typing import Tuple, List, Iterable, Sized
import pathlib as pl

"""Collection of queries for drawing together useful collections of data for analysis"""


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
    dates_to_metagames = {date: get_metagame_comp(date, length, mtg_format)
                          for date in qu.date_range(start_date, end_date, length)}
    rows = [(date, *metagame) for date, metagames in dates_to_metagames.items() for metagame in metagames]
    return pd.DataFrame(columns=['date', 'archetype', 'percentage'], data=rows)


def create_pic_dirc(format: str, start_date: str, end_date: str) -> pl.Path:
    dirc = pl.Path(f'{format}/{start_date}_to_{end_date}')
    dirc.mkdir(parents=True, exist_ok=True)
    return dirc


def spline_estimate(x: np.array, y: np.array) -> np.array:
    return spi.UnivariateSpline(x=x, y=y, k=4)(x)


def to_matplotlib_dates(dates: Iterable[str]) -> List[float]:
    return [mpd.datestr2num(date) for date in dates]


def fill_in_y_axis(all_dates: List[float], dates: List[float], y_data: np.array) -> np.array:
    date_to_data = {dates[idx]: y_data[idx] for idx in range(len(dates))}
    new_y_data = np.zeros(len(all_dates), dtype='d')
    for idx, date in enumerate(all_dates):
        new_y_data[idx] = date_to_data[date] if date in date_to_data.keys() else 0
    return new_y_data


def plot_metagame_comp(metagame_comps: pd.DataFrame, save_dirc: pl.Path) -> None:
    archetype_groups = metagame_comps.groupby('archetype')
    all_dates = to_matplotlib_dates(metagame_comps['date'])
    for archetype, group in archetype_groups:
        fig, axes = plt.subplots()
        dates = to_matplotlib_dates(group['date'])

        extended_percentages = fill_in_y_axis(all_dates, dates, list(spline_estimate(dates, group['percentage'])))

        #percentages = spline_estimate(dates, group['percentage'])

        plt.plot_date(x=all_dates, y=spline_estimate(all_dates, extended_percentages), xdate=True, linestyle='-', marker=',', color='blue')
        #plt.plot_date(x=dates, y=group['percentage'], xdate=True, linestyle='-', marker=',', color='orange')
        plt.plot_date(x=dates, y=spline_estimate(dates, group['percentage']), linestyle='-', marker=',', color='r')

        title = ' '.join([word.capitalize() for word in archetype.split(' ')])
        plt.title(title)
        plt.xlabel('Date')
        plt.ylabel('Metagame Percentage')
        plt.setp(axes.get_xticklabels(), rotation=30, horizontalalignment='right')
        plt.tight_layout()

        archetype = archetype.replace(' ', '_')
        archetype = archetype.replace('/', '\\')
        save_name = '_'.join([word.lower() for word in archetype.split(' ')])

        if save_name:
            save_path = save_dirc.joinpath(save_name)
            plt.savefig(save_path)

        plt.close(fig)


if __name__ == '__main__':
    start_date = '2018-03-13'
    end_date = '2019-05-01'
    mtg_format = 'modern'
    data = metagame_comp_over_time(start_date, end_date, 21, 'modern')
    title_path = create_pic_dirc(mtg_format, start_date, end_date)
    title = f'{{archetype}}'
    plot_metagame_comp(data, title_path)
