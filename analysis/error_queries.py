from analysis.utility import generic_search

"""Collection of queries showing errors / malformed data in the database"""

# Decks FROM mtgtop8 that have cards with a quantity greater than 4
too_many_cards = ('SELECT e.url u, c.quantity q '
                  'FROM events.event_entry e JOIN events.entry_card c ON c.entry_id = e.entry_id '
                  'HAVING q > 4 ORDER BY u, q DESC')

# Decks from mtgtop8 that have mainboards sizes greater than 60
bad_mainboards = ('SELECT e.url, SUM(c.quantity) q '
                  'FROM events.event_entry e JOIN events.entry_card c ON c.entry_id = e.entry_id '
                  'WHERE c.mainboard = \'t\' '
                  'GROUP BY e.entry_id HAVING SUM(c.quantity) > 60 ORDER BY q DESC')

# Decks from mtgtop8 that have mainboards sizes greater than 60
bad_sideboards = ('SELECT e.url, SUM(c.quantity) q '
                  'FROM events.event_entry e JOIN events.entry_card c ON c.entry_id = e.entry_id '
                  'WHERE c.mainboard = \'f\' '
                  'GROUP BY e.entry_id HAVING SUM(c.quantity) > 15 ORDER BY q DESC')

# Decks FROM mtgtop8 that have have a mislabelled card, labelled as "Unknown Card"
error_decks = ('WITH ids AS ('
               'SELECT DISTINCT(e.entry_id) id '
               'FROM events.entry_card e '
               'WHERE e.card = \'Unknown Card\') '
               'SELECT DISTINCT(e.url) '
               'FROM events.event_entry e, ids '
               'WHERE e.entry_id = ids.id')

# decks from mtgtop8 that don't have a card present in
missing_cards = ('')

if __name__ == '__main__':
    for i in generic_search(bad_sideboards):
        print(i)
