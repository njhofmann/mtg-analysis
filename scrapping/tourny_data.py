"""Module for pulling tournament data from mtgtop8.com"""
import requests
import bs4
import re

def retrieve_and_parse(url):
    url_data = requests.get(url)
    soup = bs4.BeautifulSoup(markup=url_data.text, features='html.parser')

    # get all modern tournaments
    a = soup.find_all(href=re.compile('event\?e=[0-9]+&f=MO'))
    for b in a:
        print(b)

    # for each gathered event, parse into database

if __name__ == '__main__':
    url = 'https://www.mtgtop8.com/format?f=MO&meta=92'
    retrieve_and_parse(url)