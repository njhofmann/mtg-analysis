import numpy as np
from typing import Generator, Tuple, Optional


def successive_subsets(arr: np.array, window_size: int) -> Generator[Tuple[int, np.array], None, None]:
    for i in range(arr.shape[0] - window_size):
        yield i, arr[i:i + window_size]


def empty_arr(arr: np.array, window_size: int) -> np.array:
    return np.zeros(arr.shape[0] - window_size + 1, dtype=arr.dtype)


def cumulative_moving_avg(arr: np.array) -> np.array:
    return np.cumsum(arr) / np.arange(1, arr.shape[0] + 1)


def custom_weighted_moving_avg(arr: np.array, prev_size: int, next_size: int, weights: np.array) -> np.array:
    window_size = prev_size + next_size + 1
    assert weights.shape[0] == window_size
    subsets = empty_arr(arr, window_size)
    for idx, subset in successive_subsets(arr, window_size):
        subsets[idx] = np.sum(subset * weights)  # don't divide by window size
    return subsets


def unweighted_moving_avg(arr: np.array, prev_size: int, next_size: int) -> np.array:
    window_size = prev_size + next_size + 1
    weights = np.full(shape=window_size, fill_value=(1 / window_size))
    return custom_weighted_moving_avg(arr, prev_size, next_size, weights)


def compute_one_sided_weights(side_size: int) -> np.array:
    denom = (side_size * (side_size + 1)) / 2
    return np.arange(1, side_size + 1) / denom

def compute_weights(prev_size: int, next_size: int) -> np.array:
    # sum of weights = 1
    # one sided weights
    if prev_size == 0 or next_size == 0:
        size = (prev_size if next_size == 0 else next_size) + 1
        weights = compute_one_sided_weights(size)
        return weights if next_size == 0 else np.flip(weights)

    # symmetrical sides
    if prev_size == next_size:
        long_side = max(prev_size, next_size)
        weights = np.arange(1, long_side + 2)
        weights = np.concatenate([weights, np.flip(weights[:-1])])
        size = long_side + 1
        denom = ((size * (size + 1)) / 2)
        denom = denom + (denom - size)
        return weights / denom

    # lopsided sides
    # TODO better method?
    larger, smaller = (prev_size, next_size) if prev_size > next_size else (next_size, prev_size)
    larger_weights = compute_one_sided_weights(larger)
    smaller_weights = compute_one_sided_weights(smaller)

    mean_head = (larger_weights[-1] + smaller_weights[-1]) / 2
    larger_weights = larger_weights * (mean_head / larger_weights[-1])
    smaller_weights = smaller_weights * (mean_head / smaller_weights[-1])
    lopsided_weights = np.concatenate([larger_weights, np.flip(smaller_weights[:-1])])
    return lopsided_weights / sum(lopsided_weights)


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


def central_moving_average(x: np.array, y: np.array, method: str = 'u', side_size: int = 2, recur: int = 1) -> np.array:
    return moving_average(x, y, method, prev_size=side_size, next_size=side_size, recur=recur)


def trailing_moving_avg(x: np.array, y: np.array, method: str = 'u', trailing_size: int = 4, recur: int = 1) -> np.array:
    return moving_average(x, y, method, prev_size=trailing_size, next_size=0, recur=recur)


def moving_average(x: np.array, y: np.array, method: str = 'u', prev_size: Optional[int] = 2,
                   next_size: Optional[int] = 2, recur: int = 1) -> Tuple[np.array, np.array]:
    """Performs the specified moving average over the given y axis, shifting the corresponding x axis as needed. Must
    specify the type of moving average, and the number of previous and future / next points to consider within each
    subset. Size of previous and next points to consider are ignored if method is cumulative. Can recursively apply the
    moving average.

     Ex: have pt x, if prev_size = 2 and next_size = 2, consider x-1, x-2, x+1, x+2 as the subset involving x

     Can select equally weighted (u), cumulative (c), linearly weighted (w), or exponentially weighted (e)

    :param x: x axis corresponding to given y axis
    :param y: array to perform on moving average on
    :param prev_size: number of previous points from the central point in each subset to use
    :param next_size: number of future points from central point in each subset to use
    :param method: type of moving average to perform
    :param recur: number of times to perform the moving average
    :return: array of moving averages with x axis shifted accordingly """
    assert len(x.shape) == 1 and x.shape == y.shape
    windows_size = prev_size + next_size + 1

    for _ in range(recur):

        if y.shape[0] < windows_size:
            prev_size = int(np.floor(y.shape[0] / 2))
            next_size = prev_size

        if method == 'u':  # unweighted
            x = shift_array(x, prev_size, next_size)
            y = unweighted_moving_avg(y, prev_size, next_size)
        elif method == 'w':  # linearly weighted
            x = shift_array(x, prev_size, next_size)
            y = weighted_moving_avg(y, prev_size, next_size)
        elif method == 'e':  # exponentially weighted
            x = shift_array(x, prev_size, next_size)
            y = exp_weighted_moving_avg(y, prev_size, next_size)
        elif method == 'c':  # cumulative
            y = cumulative_moving_avg(y)
        else:
            raise ValueError(f'{method} is unsupported')

    return x, y


if __name__ == '__main__':
    # TODO moving average of moving average
    a = compute_weights(3, 5)
    print(a, sum(a))
