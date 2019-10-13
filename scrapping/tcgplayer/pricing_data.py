import requests
import yaml

"""Module for pulling pricing info from TCGPlayer's API"""

# Constants
TCGPLAYER_API_URL = 'http://api.tcgplayer.com/v1.36.0'


def get_bearer_token(bearer_file):
    with open(bearer_file, 'r') as file:
        data = yaml.load(stream=file.read(), Loader=yaml.FullLoader)
        return data['token']

if __name__ == '__main__':
    print(get_bearer_token('bearer_token_info.yaml'))