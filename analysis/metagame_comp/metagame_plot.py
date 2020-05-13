import pandas as pd
import numpy as np
from typing import List, Tuple
import pathlib as pl
import analysis.moving_average as ma
import matplotlib.dates as mpd
import matplotlib.pyplot as plt
import analysis.utility as u

DEFAULT_GROUP_COUNT = 15

"""Creates a plot showing changes in metagame composition for the "top decks" in a time period for a given format"""


def select_top_decks(metagame_comps: pd.DataFrame) -> List[Tuple[str, pd.DataFrame]]:
    """Given a DataFrame of metagame compositions over time, returns the "top" decks across the whole time range of the
    DataFrame. In other words, returns the decks that have been in the metagame the longest, and have the highest
    average composition over time.
    :param metagame_comps: DataFrame of metagame compositions over time, rows consists of a date, a deck archetype, and
    that archetype's estimated metagame prevalence at that time
    :return: list of tuples of the top decks, with each tuple being a deck name and associated data
    """
    def get_time_range(group: pd.DataFrame) -> int:
        return (group['date'].max() - group['date'].min()).days

    metagame_comps = [(name, group, get_time_range(group)) for name, group in metagame_comps.groupby('archetype')]
    longest_time_range = max(map(lambda x: x[-1], metagame_comps))
    metagame_comps = filter(lambda x: x[-1] > (.9 * longest_time_range), metagame_comps)
    metagame_comps = sorted(metagame_comps, key=lambda x: x[1]['percentage'].mean(), reverse=True)
    return list(map(lambda x: (x[0], x[1]), metagame_comps))[:DEFAULT_GROUP_COUNT]


def add_other_data(top_decks: np.array) -> np.array:
    """Given a MxN array of the metagame compositions percentages of the top M decks over N periods, adds another
    numpy array to represent the metagame composition of all "other" decks at each period. When added, the sum of each
    column should equal 100.
    :param top_decks: metagame compositions percentages of the top M decks over N periods
    :return: (M+1)xN array of the metagame compositions top decks and "other" decks
    """
    other_decks = np.apply_along_axis(func1d=lambda x: 100 - np.sum(x), axis=0, arr=top_decks)
    return np.vstack([top_decks, other_decks])


def fill_in_array(array: np.array, new_size: int, start_buffer: int) -> np.array:
    """Copies a given 1D numpy array to a larger 1D numpy array of the given size. Copies the array into the new array
    with the given staring buffer. Given array must be larger than the buffer size and new array size, empty slots
    are zero
    :param array: array to copy contents over
    :param new_size: size of the new array
    :param start_buffer: how many slots after start of new array to begin copying new array over to
    :return: new array of given size with given array's contents copied over,
    """
    assert len(array.shape) == 1 and array.shape[0] > new_size + start_buffer
    if start_buffer == 0 and array.shape[0] == new_size:
        return array[:]
    new_array = np.zeros(new_size, dtype=array.dtype)
    end_idx = min(new_size, start_buffer + len(array))
    new_array[start_buffer:end_idx] = array[:]
    return new_array


def plot_metagame(metagame_comps: pd.DataFrame, save_dirc: pl.Path) -> None:
    """Given a DataFrame of metagame compositions over time, creates a plot showing the changes in metagame compositions
    for the top decks over time - saved to the given directory.
    :param metagame_comps: DataFrame of metagame compositions over time, rows consists of a date, a deck archetype, and
    that archetype's estimated metagame prevalence at that time
    :param save_dirc: directory path to save to
    :return: None
    """
    filled_groups = {}
    for name, group in select_top_decks(metagame_comps):
        group = u.fill_in_time(group, 'date', 'percentage')
        filled_groups[name] = ma.trailing_moving_avg(group['date'], group['percentage'], trail_size=45)

    longest_date = max([group[0] for group in filled_groups.values()], key=lambda x: len(x))
    filled_arrays = []
    deck_names = []
    for name, group in filled_groups.items():
        deck_names.append(name)
        start_idx = np.where(longest_date == group[0][0])[0][0]  # TODO: this can be done with simple math
        filled_arrays.append(fill_in_array(group[1], len(longest_date), start_idx))

    filled_arrays = np.vstack(filled_arrays)
    filled_arrays = add_other_data(filled_arrays)
    deck_names.append('Other Decks')
    longest_date = longest_date.apply(mpd.date2num)

    fig, ax = plt.subplots()
    ax.stackplot(longest_date, *filled_arrays, labels=deck_names)
    ax.xaxis.set_major_formatter(mpd.DateFormatter('%Y-%m-%d'))
    plt.title('Metagame Composition')
    plt.ylabel('Metagame Percentage')
    plt.xlabel('Date')
    plt.legend()
    plt.savefig(save_dirc)


def main():
    pass


if __name__ == '__main__':
    main()
