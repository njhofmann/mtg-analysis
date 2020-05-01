import analysis.utility as qu
from psycopg2 import sql
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mpd
from typing import Tuple, List
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


def plot_metagame_comp(metagame_comps: pd.DataFrame, save_dirc: pl.Path) -> None:
    archetype_groups = metagame_comps.groupby('archetype')
    for archetype, group in archetype_groups:
        dates = [mpd.datestr2num(date) for date in group['date']]
        plt.plot_date(x=dates, y=group['percentage'], xdate=True, linestyle='-', marker=',')
        plt.xlabel('Date')
        plt.ylabel('Percentage')
        title = ' '.join([word.capitalize() for word in archetype.split(' ')])
        plt.title(title)
        archetype = archetype.replace(' ', '_')
        archetype = archetype.replace('/', '\\')
        save_name = '_'.join([word.lower() for word in archetype.split(' ')])

        if save_name:
            save_path = save_dirc.joinpath(save_name)
            plt.savefig(save_path)
        plt.clf()


if __name__ == '__main__':
    start_date = '2018-03-13'
    end_date = '2019-05-01'
    mtg_format = 'modern'
    data = metagame_comp_over_time(start_date, end_date, 21, 'modern')
    title_path = create_pic_dirc(mtg_format, start_date, end_date)
    title = f'{{archetype}}'
    plot_metagame_comp(data, title_path)
