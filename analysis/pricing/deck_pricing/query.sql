WITH avg_card_prices AS (
    SELECT ei.date date, e.entry_id deck, ec.card card, AVG(pr.price) avg_price, ec.quantity quantity
    FROM events.event_entry e
        JOIN events.event_info ei
            ON ei.tourny_id = e.tourny_id
            AND ei.format = 'modern'
        JOIN events.entry_card ec
            ON ec.entry_id = e.entry_id
        JOIN cards.printings pn
            ON pn.card = ec.card
        JOIN prices.pricing pr
            ON pr.card = ec.card
            AND pr.set = pn.set
            AND pr.date = ei.date
    WHERE e.archetype = ''
    GROUP BY e.entry_id, ec.card
), deck_prices AS (
    SELECT acp.date date, SUM(acp.avg_price * acp.quantity) price
    FROM avg_card_prices acp
)
SELECT dp.date, AVG(dp.price)
FROM deck_prices AS dp
GROUP BY dp.date