### MTGTop8 parser
* production vs dev mode
    * prod: kill parsing for format when dup entry detected
    * dev: keep parsing over any dup entries
* pioneer scrapping
* upto date scrapping for existing formats
* automatically stopping parsing (errors?)
* header file for scrapper
* combine list comprehensions / turn into functions

### MTG Goldfish Scrapper
* get prices from last few months

### DB Schemas
* Add format periods and legal blocks
* Table desps how?
* Remove '-' type key
* Update changes across project
* Major vs non major events
* Online vs paper events
* Update database tables and namings

### TCGPlayer
* look into drawing prices for 

### Docker
* dockerize data scrappers
* run scrappers in order
* connect to outside db
* automated docker compose file (keep order in mind_)

### Style
* data types
* f-strings
* sql format calls, one per line

### misc
* get tcgplayer api key
* Redo entries for "unknown cards"
* Documentation
* DB names constants file
* Rename tables and keys
* automatic data backups? external storage?
* Questions of interest --> needed data --> relevant SQL query

* How to build data sheet
* Constants file
* What queries to run to gather data
