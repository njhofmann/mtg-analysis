# mtg-analysis
Time series analysis and prediction of competitive level play and card prices for Magic: The Gathering.

# Motivation
This project aims to provide a comprehensive database combining tournament level metagame data, card prices, and card 
info (CMC, printed sets, types, etc.). In addition to a series of investigations carried out on said data motivated by the 
following questions:

* How have the prices for cards and decks in non-rotating formats changed over time?
* How have format metagame compositions changed over time? Can they be predicted using current metagame compositions?
* How does a card seeing more or less play overtime impact its price? 
* What impact do reprints have on the price of MTG cards? Can this impact be predicted?

# Setup
This project was build using Python 3.8 and the libraries listed under `requirements.txt`. They can be installed with 
`pip install -r requirements.txt`.

The source root directory this project was built on is the parent directory where all top level files and subdirectories,
such as the `README.md` reside. Any scripts that are run should be run as modules formatted like `python -m path.to.script
insert_arguments_here` (dots instead of back slashes, drop the .py extension).

### Building the Database
The size of the database is larger than the free tier of GitHub's Large File Storage, so to acquire a copy of the
for your own purposes - the following must be done:

1. Setup Python environment as described above
1. Install [Postgres 11](https://www.postgresql.org/) 
1. One of the following:
    1. Request a dump of the database from myself via Github or one of my other contact points. Load the dump into the database with `database/db_init.py`. This creates a new database with data intact.
    1. Initialize a blank copy of the database under `database/db_init.py`, after having installed Postgres. Repopulate the database by rerunning the scrapping scripts under `scrapping/scrap_all.py`.

Fair warning, attempting to repopulate the database manually may take upwards of 1-2 days, depending on the capabilities 
of your system. Recommended you adjust the multiprocessing parameters of each scrapper, the more the faster scrapping 
will go.

The configuration info used for the database is under `database/db-config.yaml`. Read `database/db_init.py` for instructions on how to run the script

# Directories
#### Database
This directory contains all the scripts and other supporting files necessary for setting up a blank version of the
database, backing up an existing version of the database, and loading login info. More information can be found in the 
documentation of each file under this subdirectory.

#### Scrapping
The directory contains all the scripts necessary for rebuilding or updating the database by scrapping and parsing the 
appropriate sites, and saving their data in the database. More info can be found in the documentation of each file under
this subdirectory.  

#### Analysis
This directory contains all the scripts necessary for recreating the analyses attempting to answer the motivating 
questions of this project. More info can be found in the documentation of each file under this subdirectory, as well 
as in the process reports for each analysis underlying it's assumptions and usage.  

# Licensing
This project's code and data are completely free to use, modify, copy, or redistribute under the GPL3 license. However 
due to the size of the database a copy is not hosted on Github, but copies are available per request. 

# Accreditations
### 3rd Party Libraries
* Data storage and interfacing provided by [Postgres 11.5](https://www.postgresql.org/) and [psycopg2 2.3.8](https://pypi.org/project/psycopg2/).
* Web scrapping and API calls with [Requests](https://2.python-requests.org/en/master/) and [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/).
* Data visualization provided by [Matplotlib](https://matplotlib.org/).
* Machine learning and related utilities provided by [Sci-Kit Learn](https://scikit-learn.org/stable/) and [SciPy](https://www.scipy.org/) 

### Data Sources
* Tournament data from [mtgtop8](mtgtop8.com).
* Pricing data from [MTGGoldfish](mtggoldfish.com)
* Card info from the [Scryfall API](https://scryfall.com/docs/api).

