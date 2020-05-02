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


def extend_y_data(all_dates: List[float], dates: List[float], y_data: np.array) -> Tuple[np.array, np.array]:
    min_date = min(all_dates)  # TODO [0], [-1]?
    max_date = max(all_dates)
    sorted_dates = sorted(all_dates)

    def float_eq(a: float, b: float) -> bool:
        return abs(a - b) < .00001

    def in_dates(num: float) -> bool:
        for item in dates:
            if float_eq(item, num):
                return True
        return False

    def get_idx(num: float) -> int:
        for idx, item in enumerate(sorted_dates):
            if float_eq(item, num):
                return idx
        else:
            raise ValueError(f'{num} not present in all dates')

    def get_min_mid_pt() -> float:
        min_date_idx = get_idx(min(dates))
        mid_pt_idx = round(.5 * min_date_idx)
        if float_eq(min_date_idx, mid_pt_idx) or float_eq(mid_pt_idx, 0):
            return -1
        return all_dates[mid_pt_idx]

    def get_max_mid_pt() -> float:
        max_mid_pt = get_idx(max(dates))
        end_idx = len(sorted_dates) - 1
        mid_pt_idx = min(round(1.5 * max_mid_pt), end_idx)
        if float_eq(max_mid_pt, mid_pt_idx) or float_eq(mid_pt_idx, end_idx):
            return -1
        return all_dates[mid_pt_idx]

    has_min = in_dates(min_date)
    has_max = in_dates(max_date)

    if has_min and has_max:
        return y_data, dates

    min_added = True
    other_dates = dates.copy()
    min_buffer = 1
    if not has_min and not has_max:
        count = 2
        mind_mid_date = get_min_mid_pt()
        if mind_mid_date >= 0:
            count += 1

        max_mid_date = get_max_mid_pt()
        if max_mid_date >= 0:
            count += 1

        if count == 2:
            other_dates = [min_date] + other_dates + [max_date]
        elif count == 4:
            other_dates = [min_date, mind_mid_date] + other_dates + [max_mid_date, max_date]
        elif mind_mid_date >= 0:
            other_dates = [min_date, mind_mid_date] + other_dates + [max_date]
        else:
            other_dates = [min_date] + other_dates + [max_mid_date, max_date]

        new_y_data = np.zeros(len(y_data) + count)
    else:
        count = 1
        if not has_min:
            min_mid_pt = get_min_mid_pt()
            if min_mid_pt >= 0:
                count += 1
                other_dates = [min_date, min_mid_pt] + other_dates
            else:
                other_dates = [min_date] + other_dates
        else:
            max_mid_pt = get_max_mid_pt()
            if max_mid_pt >= 0:
                count += 1
                other_dates = other_dates + [max_mid_pt, max_date]
            else:
                other_dates.append(max_date)
            min_added = False

        new_y_data = np.zeros(len(y_data) + count)

    for idx, item in enumerate(y_data):
        if min_added:
            idx += min_buffer
        new_y_data[idx] = item

    return new_y_data, other_dates


def plot_metagame_comp(metagame_comps: pd.DataFrame, save_dirc: pl.Path) -> None:
    archetype_groups = metagame_comps.groupby('archetype')
    all_dates = to_matplotlib_dates(metagame_comps['date'])
    plot_args = {'linestyle': '-', 'marker': ',', 'xdate': True}
    for archetype, group in archetype_groups:
        fig, axes = plt.subplots()
        dates = to_matplotlib_dates(group['date'])
        percents = group['percentage'].to_numpy(dtype=np.float)

        fitted_percents = spline_estimate(dates, percents)
        extended_percentages, some_dates = extend_y_data(all_dates, dates, percents)
        fitted_extended_percents = spline_estimate(some_dates, extended_percentages)

        axes.plot_date(x=dates, y=percents, color='r', label='Raw Points', **plot_args)
        axes.plot_date(x=dates, y=fitted_percents, color='orange', label='Fitted Points', **plot_args)
        axes.plot_date(x=some_dates, y=fitted_extended_percents, color='purple', label='Extended Fitted Points', **plot_args)
        axes.legend()

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
