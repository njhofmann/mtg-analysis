--decks FROM mtgtop8 that have have a mislabelled card, labelled as "Unknown Card"
WITH ids AS (
    SELECT DISTINCT(e.entry_id) id
    FROM events.entry_card e
    WHERE e.card = 'Unknown Card'
)
SELECT DISTINCT(e.url)
FROM events.event_entry e, ids
WHERE e.entry_id = ids.id