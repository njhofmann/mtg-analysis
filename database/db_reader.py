import yaml
import pathlib as pl

"""Module for reading in database configuration info such as database name, login username, password, and other info"""

with open('db-config.yaml', 'r') as config:
    db_info = yaml.load(config, Loader=yaml.FullLoader)
    DATABASE_NAME = db_info['DATABASE']
    USER = db_info['OWNER']
    PASSWORD = db_info['PASSWORD']
