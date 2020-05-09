WITH price_sets AS (
    SELECT DISTINCT(set) price_set FROM prices.pricing
),
card_sets AS (
    SELECT DISTINCT(set) card_set FROM cards.set_info
)
SELECT DISTINCT(s.full_name)
FROM card_sets c
    LEFT JOIN price_sets p
        ON p.price_set = c.card_set
    JOIN cards.set_info s
        ON s.set = c.card_set
WHERE p.price_set IS NULL
ORDER BY s.full_name