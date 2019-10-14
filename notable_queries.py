"""Collection of notable queries"""

url_to_deck_size = 'select e.url, sum(c.quantity) q from events.event_entry e join events.entry_card c on c.entry_id = e.entry_id group by e.entry_id having sum(c.quantity) > 60 sum(c.quantity) order by q desc'

error_decks = 'with ids as (select distinct(e.entry_id) id from events.entry_card e where e.card = \'Unknown Card\') select distinct(e.url) from events.event_entry e, ids where e.entry_id = ids.id'
