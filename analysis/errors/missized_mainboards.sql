--mtgtop8 decks that have mainboards with more than 60 cards
SELECT e.url, SUM(c.quantity) q
FROM events.event_entry e
    JOIN events.entry_card c
        ON c.entry_id = e.entry_id
WHERE c.mainboard = 't'
GROUP BY e.entry_id
HAVING SUM(c.quantity) > 60
ORDER BY q DESC