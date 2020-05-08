SELECT pr.date, pr.price, s.full_name, s.release, pn.rarity
FROM prices.pricing pr
    JOIN cards.set_info s
        ON pr.set = s.set
    JOIN cards.printings pn
        ON s.set = pn.set
        AND pn.card = pr.card
WHERE pr.card = '{card}'
AND pr.is_paper = '{paper}';
