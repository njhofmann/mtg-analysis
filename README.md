# mtg-analysis
Data analysis and modeling of competitive level play and card prices for Magic: The Gathering, over time.

# Motivating Questions

* What is the relationship between the price of new MTG cards (hype / chase cards vs sleeper / overlooked cards) over time in relation to their subsequent prevalence in relevant metagames?

* How much does a card seeing play after its release impact its price? 

* If card was already predicted to be played, how does its price change? 

* If card was a sleeper, how much does its price change?

* How much of an impact do reprints have on the price of MTG cards over time? 

* If a card is reprinted, how does print size relate to price decline? 

* How long does it take for the price to rebound to pre-reprint levels?

* Etc.



# 3D Party Libraries
* Data stored with [Postgres 11.5](https://www.postgresql.org/)
* Database interfacing with [psycopg2 2.3.8](https://pypi.org/project/psycopg2/).

# Data Acknowledgements
* Tournament data drawn from [mtgtop8.com](mtgtop8.com).
* Financial data drawn from ...
* Card info drawn from the [Scryfall API](Scryfall API).
