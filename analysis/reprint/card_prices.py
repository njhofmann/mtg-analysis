import sys
import matplotlib.pyplot as plt
import matplotlib.dates as mbd
import analysis.utility as u
import analysis.reprint.load_df as ld


def plot_card_prices(card: str, is_paper: bool) -> None:
    data = ld.get_price_and_reprint_info(card, is_paper).drop('rarity', axis=1)
    price_data = data[['price_date', 'price', 'set']]
    set_data = data[['set', 'release_date']].drop_duplicates(subset='set')

    set_data['release_date'] = set_data['release_date'].apply(mbd.date2num)

    earliest_date = mbd.date2num(data['price_date'].min())
    lowest_price = min(price_data['price'].min(), 0)
    highest_price = price_data['price'].max()

    for idx, row in set_data.iterrows():
        if row['release_date'] >= earliest_date:
            plt.vlines(x=row['release_date'], ymin=lowest_price, ymax=highest_price, label=row['set'] + ' Release',
                       linestyles='solid')

    for name, release_group in price_data.groupby('set'):
        price_dates = release_group['price_date'].apply(mbd.date2num)
        plt.plot_date(x=price_dates, y=release_group['price'], label=name, **u.PLOT_ARGS)

    date_prices = price_data.groupby('price_date').agg(func='mean')
    prices = list(map(mbd.date2num, date_prices.index))
    plt.plot_date(x=prices, y=date_prices['price'], label='Average Price', **u.PLOT_ARGS)

    plt.title(f'{card} {"Paper" if is_paper else "Online"} Prices')
    plt.legend()
    plt.ylabel('Price')
    plt.xlabel('Date')
    plt.show()
    # TODO finish me


def main():
    args = sys.argv
    if len(args) < 3:
        name = args[0].split('/')[-1]
        raise ValueError(f'usage: {name} card_name paper_prices')

    true_args = ('t', 'T', 'true', 'True')
    false_args = ('f', 'F', 'false', 'False')
    if args[-1] not in true_args + false_args:
        raise ValueError(f'valid paper_prices args are {true_args} and {false_args}')

    bool_arg = True if args[-1] in true_args else False
    card_name = ' '.join(args[1:-1])
    plot_card_prices(card_name, bool_arg)


if __name__ == '__main__':
    main()
