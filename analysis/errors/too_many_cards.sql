--mtgtop8 decks that have more than 4 of one cards
WITH basic_lands AS (
    SELECT DISTINCT(t.card) card
    FROM cards.types t
    WHERE t.type = 'basic'
)
SELECT e.url u, c.quantity q
FROM events.event_entry e
    JOIN events.entry_card c
        ON c.entry_id = e.entry_id
    JOIN cards.types t
        ON t.card = c.card
WHERE c.quantity > 4
AND c.card NOT IN (SELECT card FROM basic_lands)
ORDER BY q DESC