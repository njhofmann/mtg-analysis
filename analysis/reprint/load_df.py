import pandas as pd
import analysis.utility as u


def get_price_and_reprint_info(card: str, paper_prices: bool) -> pd.DataFrame:
    paper = 't' if paper_prices else 'f'
    query = u.load_query('query.sql').format(card=card, paper=paper)
    sql_data = u.generic_search(query)
    data_frame = pd.DataFrame(sql_data, columns=['price_date', 'price', 'set', 'release_date', 'rarity'])
    data_frame['price_date'] = pd.to_datetime(data_frame['price_date'])  # set as date type
    data_frame['release_date'] = pd.to_datetime(data_frame['release_date'])  # set as date type
    data_frame['price'] = pd.to_numeric(data_frame['price'].apply(func=lambda x: x.replace('$', '')))  # money to float
    return data_frame


if __name__ == '__main__':
    print(get_price_and_reprint_info('Dark Confidant', True))
