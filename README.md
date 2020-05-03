# mtg-analysis
Time series analysis and modeling of competitive level play and card prices for Magic: The Gathering.

# Motivating Questions

* How have the prices for decks in non-rotating formats changed over time?

* How have format metagames changed over time?

* What is the relationship between the price of new MTG cards (hype / chase cards vs sleeper / overlooked cards) over 
time in relation to their subsequent prevalence in relevant metagames?

* How much does a card seeing more or less play in a metagame impact its price? 

* How much of an impact do reprints have on the price of MTG cards over time? How does print size and rarity relate to 
price decline?  How long does it take for the price to rebound to pre-reprint levels?

# Contributions

* Unified database of MTG tournament results, prices, and card info.

* Visualization and prediction of for competitive metagame composition, pricing, reprints, and other areas.

# 3rd Party Libraries
* Data storage and interfacing provided by [Postgres 11.5](https://www.postgresql.org/) and [psycopg2 2.3.8](https://pypi.org/project/psycopg2/).
* Web scrapping and API calls with [Requests](https://2.python-requests.org/en/master/) and [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/).``
* Data visualization provided by [Matplotlib](https://matplotlib.org/).

# Data Sources
* Tournament data from [mtgtop8](mtgtop8.com).
* Pricing data from [MTGGoldfish](mtggoldfish.com)
* Card info from the [Scryfall API](https://scryfall.com/docs/api).
