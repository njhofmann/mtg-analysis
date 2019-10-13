import requests
import ast
import yaml

"""Requests a new bearer token from the TCGPlayer API to request data from the TCGPlayer API"""

# Constants
TCGPLAYER_TOKEN_URL = 'https://api.tcgplayer.com/token'

def get_new_bearer_token(tcgplayer_info, bearer_info):
    """
    Requests a new bearer token from the TCGPlayer API using the private and public keys listed under
    'tcgplayer_info.yaml'. Stores the new bearer token and related info under 'bearer_token_info.yaml'.
    :
    :return: None
    """
    with open(tcgplayer_info, 'r') as key_info:
        key_data = yaml.load(stream=key_info.read(), Loader=yaml.FullLoader)

    public_key = key_data['public_key']
    private_key = key_data['private_key']

    header = 'application/x-www-form-urlencoded'
    data = f'grant_type=client_credentials&client_id={public_key}&client_secret={private_key}'
    response = requests.post(url=TCGPLAYER_TOKEN_URL, data=data.encode())

    if not response.ok:
        response.raise_for_status()

    # convert bytes to python dict
    bearer_bytes = response.content
    bearer_dict = ast.literal_eval(bearer_bytes.decode(encoding='utf-8'))

    bearer_dict = {'token': bearer_dict['access_token'],
                   'username': bearer_dict['userName'],
                   'issued': bearer_dict['.issued'],
                   'expires': bearer_dict['.expires']}

    bearer_yaml = yaml.dump(data=bearer_dict, Dumper=yaml.Dumper)

    with open(bearer_info, 'w') as file:
        file.write(bearer_yaml)


if __name__ == '__main__':
    get_new_bearer_token('tcgplayer_info.yaml', 'bearer_token_info.yaml')