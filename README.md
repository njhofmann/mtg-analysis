# mtg-analysis
Data analysis and modeling of competitive level play and card prices for Magic: The Gathering, over time.

# Motivating Questions

* What is the relationship between the price of new MTG cards (hype / chase cards vs sleeper / overlooked cards) over 
time in relation to their subsequent prevalence in relevant metagames?

* How much does a card seeing more or less play in a metagame impact its price? 

* How much of an impact do reprints have on the price of MTG cards over time? How does print size and rarity relate to 
price decline?  How long does it take for the price to rebound to pre-reprint levels?

* How have the prices for decks in non-rotating formats changed over time?

# 3D Party Libraries
* Data stored with [Postgres 11.5](https://www.postgresql.org/)
* Database interfacing with [psycopg2 2.3.8](https://pypi.org/project/psycopg2/).
* Web scrapping and API calls done with [Requests](https://2.python-requests.org/en/master/) and [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/).

# Data Acknowledgements
* Tournament data drawn from [mtgtop8.com](mtgtop8.com).
* Financial data drawn from [MTGGoldfish](mtggoldfish.com)
* Card info drawn from the [Scryfall API](https://scryfall.com/docs/api).
