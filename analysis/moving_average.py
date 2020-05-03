import numpy as np
from typing import Generator, Tuple, Optional


def successive_subsets(arr: np.array, window_size: int) -> Generator[Tuple[int, np.array], None, None]:
    for i in range(arr.shape[0] - window_size):
        yield i, arr[i:i + window_size]


def empty_arr(arr: np.array, window_size: int) -> np.array:
    return np.zeros(arr.shape[0] - window_size + 1, dtype=arr.dtype)


def cumulative_moving_avg(arr: np.array) -> np.array:
    sums = empty_arr(arr, 1)
    for idx in range(arr.shape[0]):
        if idx == 0:
            sums[0] = arr[0]
        else:
            sums[idx] = sums[idx - 1] + ((arr[idx] - sums[idx - 1]) / (idx + 1))
    return sums


def custom_weighted_moving_avg(arr: np.array, prev_size: int, next_size: int, weights: Optional[np.array]) -> np.array:
    window_size = prev_size + next_size + 1

    if weights:
        assert weights.shape[0] == window_size

    subsets = empty_arr(arr, window_size)
    for idx, subset in successive_subsets(arr, window_size):
        if weights:
            subset *= weights
        subsets[idx] = np.sum(subset) / window_size
    return subsets


def unweighted_moving_avg(arr: np.array, prev_size: int, next_size: int) -> np.array:
    return custom_weighted_moving_avg(arr, prev_size, next_size, None)


def compute_weights(prev_size: int, next_size: int) -> np.array:
    # sum of weights = 1

    # one sided weights
    if prev_size == 0 or next_size == 0:
        size = (prev_size if next_size == 0 else next_size) + 1
        denom = (size * (size + 1)) / 2
        weights = np.arange(1, size+1) / denom
        return weights if next_size == 0 else np.flip(weights)

    # symmetrical sides
    if prev_size == next_size:
        weights = np.arange(1, prev_size+2)
        print(weights)
        weights = np.concatenate([weights, np.flip(weights[:-1])])
        size = prev_size + 1
        denom = ((size * (size + 1)) / 2)
        denom = denom + (denom - size)
        #denom = (size * (size + 1)) / 2
        return weights / denom

    # lopsided sides


def weighted_moving_avg(arr: np.array, prev_size: int, next_size: int) -> np.array:
    weights = compute_weights(prev_size, next_size)
    return custom_weighted_moving_avg(arr, prev_size, next_size, weights)


def exp_weighted_moving_avg(arr: np.array, prev_size: int, next_size: int):
    pass


def shift_array(arr: np.array, prev_size: int, next_size: int) -> np.array:
    assert prev_size >= 0 and next_size >= 0
    if prev_size == 0 and next_size == 0:
        return arr
    elif prev_size == 0:
        return arr[:-next_size]
    elif next_size == 0:
        return arr[prev_size:]
    return arr[prev_size:-next_size]


def central_moving_average(x: np.array, y: np.array, method: str = 'u', side_size: int = 2) -> np.array:
    return moving_average(x, y, method, prev_size=side_size, next_size=side_size)


def trailing_moving_avg(x: np.array, y: np.array, method: str = 'u', trailing_size: int = 4) -> np.array:
    return moving_average(x, y, method, prev_size=trailing_size, next_size=0)


def moving_average(x: np.array, y: np.array, method: str = 'u', prev_size: Optional[int] = 2,
                   next_size: Optional[int] = 2) -> Tuple[np.array, np.array]:
    """
    :param arr: array to perform on
    :param prev_size: number of previous points from the central point in each subset to use
    :param next_size: number of future points from central point in each subset to use
    :param method: type of moving average to perform
    :return: array of moving averages"""
    windows_size = prev_size + next_size + 1
    if method == 'u':  # unweighted
        return shift_array(x, prev_size, next_size), unweighted_moving_avg(y, prev_size, next_size)
    elif method == 'w':  # linearly weighted
        return shift_array(x, prev_size, next_size), weighted_moving_avg(y, prev_size, next_size)
    elif method == 'ew':  # exponentially weighted
        return shift_array(x, prev_size, next_size), exp_weighted_moving_avg(y, prev_size, next_size)
    elif method == 'c':  # cumulative
        return x, cumulative_moving_avg(y)
    else:
        raise ValueError(f'{method} is unsupported')


if __name__ == '__main__':
    a = compute_weights(3, 3)
    print(a, sum(a))
