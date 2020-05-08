import sys
import analysis.utility as au
import analysis.moving_average as ma
import pandas as pd
import pathlib as pl
import matplotlib.pyplot as plt
from typing import Tuple, List

"""Module for displaying trends in deck prices over time"""


def get_deck_prices(mtg_format: str, archetype: str) -> pd.DataFrame:
    # get raw data
    query = au.load_query('query.sql').format(format=mtg_format, archetype=archetype)
    results = au.generic_search(query)

    # data frame with correct column types
    data_frame = pd.DataFrame(results, columns=['date', 'price'])
    data_frame['price'] = pd.to_numeric(data_frame['price'])
    data_frame['date'] = pd.to_datetime(data_frame['date'])

    # set date as index, interpolate missing dates & prices
    data_frame = data_frame.set_index(pd.DatetimeIndex(data_frame['date']))
    data_frame = data_frame.resample('D').asfreq()
    data_frame['date'] = data_frame.index
    data_frame['price'] = data_frame['price'].interpolate('time')
    return data_frame


def get_save_dirc() -> pl.Path:
    dirc = pl.Path('results')
    dirc.mkdir(parents=True, exist_ok=True)
    return dirc


def plot_data(data_frame: pd.DataFrame, title: str) -> None:
    x = data_frame['date']
    y = data_frame['price']
    averaged_data = ma.central_moving_average(x, y, method='u', side_size=35)

    plt.plot_date(x=x, y=y, label='Raw Data', color='r', **au.PLOT_ARGS)
    plt.plot_date(*averaged_data, label='Moving Average', color='blue', **au.PLOT_ARGS)

    plt.title(title)
    plt.legend()
    plt.xlabel('Date')
    plt.ylabel('Price')

    save_name = get_save_dirc().joinpath('_'.join([word.lower() for word in title.split(' ')]))
    plt.savefig(save_name)


def main():
    args = sys.argv
    if len(args) < 3:
        raise ValueError(f'usage: {args[0]}.py format archetype')
    mtg_format = args[1]
    deck_name = ' '.join(args[2:])
    archetype = deck_name + ' decks'
    data_frame = get_deck_prices(mtg_format, archetype)
    plot_title = mtg_format.capitalize() + ' ' + deck_name + ' Deck Prices'
    plot_data(data_frame, plot_title)


if __name__ == '__main__':
    main()
