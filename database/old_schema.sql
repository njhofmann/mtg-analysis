CREATE SCHEMA cards;

CREATE SCHEMA events;

CREATE SCHEMA prices;

CREATE TYPE events.format AS ENUM (
    'standard',
    'modern',
    'legacy'
);

CREATE TABLE events.format_period (
    id SERIAL NOT NULL,
    format FORMAT,
    start DATE,
    end DATE,
    UNIQUE (format, start, end)
)

CREATE TABLE events.event_info (
    event_id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    date DATE NOT NULL,
    format FORMAT NOT NULL,
    /* may not be recorded */
    size INTEGER,
    url TEXT NOT NULL,
    /* entirely possible to have tournaments with same name on same day in same format */
    UNIQUE (name, date, format, url)
);

CREATE TABLE events.event_entry (
    event_id INTEGER NOT NULL,
    entry_id SERIAL,
    archetype TEXT NOT NULL,
    place TEXT NOT NULL,
    player TEXT NOT NULL,
    deck_name TEXT NOT NULL,
    url TEXT NOT NULL,
    PRIMARY KEY (entry_id),
    UNIQUE (tourny_id, archetype, place, player),
    FOREIGN KEY (tourny_id) REFERENCES tournament_info (tourny_id)
);

CREATE TABLE events.entry_card (
    entry_id INTEGER NOT NULL,
    card TEXT NOT NULL,
    mainboard BOOLEAN NOT NULL,
    quantity INTEGER NOT NULL,
    CONSTRAINT positive_quantity CHECK (quantity > 0),
    PRIMARY KEY (entry_id, card, mainboard),
    FOREIGN KEY (entry_id) REFERENCES events.event_entry (entry_id)
);

CREATE TABLE prices.pricing (
    card TEXT,
    set TEXT,
    date DATE,
    is_paper BOOLEAN,
    price MONEY NOT NULL,
    PRIMARY KEY (card, set, date, is_paper)
);

CREATE TYPE cards.color AS ENUM (
    'w', -- white
    'u', -- blue
    'b', -- black
    'r', -- red
    'g', -- green
    'c' -- colorless
);

CREATE TABLE cards.set_info (
    set TEXT PRIMARY KEY,
    full_name TEXT NOT NULL,
    release DATE NOT NULL,
    size INTEGER NOT NULL
);


CREATE TABLE events.format_period_set (
    period_id INTEGER,
    set TEXT,
    PRIMARY KEY (period_id, set),
    FOREIGN KEY (set) REFERENCES cards.set_info(set)
)


CREATE TABLE cards.colors (
    card TEXT,
    color COLOR,
    PRIMARY KEY (card, color)
);

CREATE TABLE cards.types (
    card TEXT,
    type TEXT,
    PRIMARY KEY (card, type)
);

CREATE TABLE cards.cmc (
    card TEXT PRIMARY KEY,
    cmc INTEGER NOT NULL,
    CONSTRAINT positive_quantity CHECK (cmc >= 0)
);

CREATE TABLE cards.pt (
    card TEXT PRIMARY KEY,
    power TEXT NOT NULL,
    toughness TEXT NOT NULL
);

CREATE TABLE cards.text (
    card TEXT PRIMARY KEY,
    text TEXT NOT NULL
);

CREATE TABLE cards.printings (
    card TEXT,
    set TEXT NOT NULL,
    PRIMARY KEY (card, set),
    FOREIGN KEY (set) REFERENCES cards.set_info (set)
);
