# mtg-analysis
Time series analysis and modeling of competitive level play and card prices for Magic: The Gathering.

# Motivating Questions
* How have the prices for decks in non-rotating formats changed over time?
* How have format metagames changed over time?
* Can future metagame compositions be predicted using current metagame compositions?
* How does a card seeing more or less play in a metagame overtime impact its price? 
* What impact do reprints have on the price of MTG cards over time? Can this impact be predicted?

# 3rd Party Libraries
* Data storage and interfacing provided by [Postgres 11.5](https://www.postgresql.org/) and [psycopg2 2.3.8](https://pypi.org/project/psycopg2/).
* Web scrapping and API calls with [Requests](https://2.python-requests.org/en/master/) and [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/).``
* Data visualization provided by [Matplotlib](https://matplotlib.org/).

# Data Sources
* Tournament data from [mtgtop8](mtgtop8.com).
* Pricing data from [MTGGoldfish](mtggoldfish.com)
* Card info from the [Scryfall API](https://scryfall.com/docs/api).

# Usage
This project's code and data are completely free to use under the GPL3 license. However due to the size of the data it is not hosted on Github, but copies are available on request. 
