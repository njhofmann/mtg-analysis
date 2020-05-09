--mtgtop8 decks that have sideboards with more than 15 cards
SELECT e.url, SUM(c.quantity) q
FROM events.event_entry e
    JOIN events.entry_card c
        ON c.entry_id = e.entry_id
WHERE c.mainboard = 'f'
GROUP BY e.entry_id
HAVING SUM(c.quantity) > 15
ORDER BY q DESC