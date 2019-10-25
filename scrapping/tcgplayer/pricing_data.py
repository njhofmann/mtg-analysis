import requests
import yaml

"""Module for pulling pricing info from TCGPlayer's API"""

# Constants
TCGPLAYER_API_URL = 'http://api.tcgplayer.com/v1.36.0'
MTG_CATEGORY_ID = 1
CATEGORIES_ENDPOINT = TCGPLAYER_API_URL + '/catalog/categories'
MANIFEST_ENDPOINT = TCGPLAYER_API_URL + f'/catalog/categories/{MTG_CATEGORY_ID}/search/manifest'


def get_categories(bearer_token, limit=100, offset=0):
    headers = {'Authorization': f'bearer {bearer_token}'}
    params = {'limit': str(limit), 'offset': str(offset)}
    data = requests.get(url=CATEGORIES_ENDPOINT, headers=headers, params=params).json()

    id_to_name = {}
    for result in data['results']:
        id_to_name[result['categoryId']] = result['displayName']
    return id_to_name


def get_bearer_token(bearer_file):
    with open(bearer_file, 'r') as file:
        data = yaml.load(stream=file.read(), Loader=yaml.FullLoader)
        return data['token']


if __name__ == '__main__':
    bearer_token = get_bearer_token('bearer-token-info.yaml')
    print(get_categories(bearer_token))