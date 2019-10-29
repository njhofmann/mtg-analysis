import yaml
import pathlib as pl

"""Module for reading in database configuration info such as database name, login username, password, and other info"""

config_path = pl.Path(__file__).parent.joinpath('db-config.yaml').resolve()
with open(config_path, 'r') as config:
    db_info = yaml.load(config, Loader=yaml.FullLoader)
    DATABASE_NAME = db_info['DATABASE']
    USER = db_info['OWNER']
    PASSWORD = db_info['PASSWORD']