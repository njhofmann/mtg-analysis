WITH avg_card_prices AS (
    SELECT ei.date date, e.entry_id deck, AVG(pr.price::numeric * ec.quantity) avg_price
    FROM events.event_entry e
        JOIN events.event_info ei
            ON ei.tourny_id = e.tourny_id
            AND ei.format = '{format}'
        JOIN events.entry_card ec
            ON ec.entry_id = e.entry_id
        JOIN cards.printings pn
            ON pn.card = ec.card
        JOIN prices.pricing pr
            ON pr.card = ec.card
            AND pr.set = pn.set
            AND pr.date = ei.date
    WHERE e.archetype = '{archetype}'
    GROUP BY ei.date, e.entry_id, ec.card
), deck_prices AS (
    SELECT acp.date date, SUM(acp.avg_price) price
    FROM avg_card_prices acp
    GROUP BY acp.date, acp.deck
)
SELECT dp.date, AVG(dp.price::numeric)
FROM deck_prices AS dp
GROUP BY dp.date
ORDER BY dp.date