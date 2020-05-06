SELECT pr.date, pr.price, pr.set, s.release, pn.rarity
FROM prices.pricing pr
    JOIN cards.set_info s
        ON pr.set = s.set
    JOIN cards.printings pn
        ON s.set = pn.set
        AND pn.card = pr.card
WHERE pr.card = {};
