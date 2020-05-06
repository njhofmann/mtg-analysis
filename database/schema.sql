--
-- PostgreSQL database dump
--

-- Dumped from database version 11.7
-- Dumped by pg_dump version 11.7

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: cards; Type: SCHEMA; Schema: -; Owner: postgres
--

CREATE SCHEMA cards;


ALTER SCHEMA cards OWNER TO postgres;

--
-- Name: events; Type: SCHEMA; Schema: -; Owner: postgres
--

CREATE SCHEMA events;


ALTER SCHEMA events OWNER TO postgres;

--
-- Name: prices; Type: SCHEMA; Schema: -; Owner: postgres
--

CREATE SCHEMA prices;


ALTER SCHEMA prices OWNER TO postgres;

--
-- Name: color; Type: TYPE; Schema: cards; Owner: postgres
--

CREATE TYPE cards.color AS ENUM (
    'w',
    'u',
    'b',
    'r',
    'g',
    'c'
);


ALTER TYPE cards.color OWNER TO postgres;

--
-- Name: format; Type: TYPE; Schema: events; Owner: postgres
--

CREATE TYPE events.format AS ENUM (
    'standard',
    'modern',
    'legacy',
    'pioneer'
);


ALTER TYPE events.format OWNER TO postgres;

SET default_tablespace = '';

SET default_with_oids = false;

--
-- Name: cmc; Type: TABLE; Schema: cards; Owner: postgres
--

CREATE TABLE cards.cmc (
    card text NOT NULL,
    cmc integer NOT NULL,
    CONSTRAINT positive_quantity CHECK ((cmc >= 0))
);


ALTER TABLE cards.cmc OWNER TO postgres;

--
-- Name: colors; Type: TABLE; Schema: cards; Owner: postgres
--

CREATE TABLE cards.colors (
    card text NOT NULL,
    color cards.color NOT NULL
);


ALTER TABLE cards.colors OWNER TO postgres;

--
-- Name: printings; Type: TABLE; Schema: cards; Owner: postgres
--

CREATE TABLE cards.printings (
    card text NOT NULL,
    set text NOT NULL
);


ALTER TABLE cards.printings OWNER TO postgres;

--
-- Name: pt; Type: TABLE; Schema: cards; Owner: postgres
--

CREATE TABLE cards.pt (
    card text NOT NULL,
    power text NOT NULL,
    toughness text NOT NULL
);


ALTER TABLE cards.pt OWNER TO postgres;

--
-- Name: set_info; Type: TABLE; Schema: cards; Owner: postgres
--

CREATE TABLE cards.set_info (
    set text NOT NULL,
    full_name text NOT NULL,
    release date NOT NULL,
    size integer NOT NULL
);


ALTER TABLE cards.set_info OWNER TO postgres;

--
-- Name: text; Type: TABLE; Schema: cards; Owner: postgres
--

CREATE TABLE cards.text (
    card text NOT NULL,
    text text NOT NULL
);


ALTER TABLE cards.text OWNER TO postgres;

--
-- Name: types; Type: TABLE; Schema: cards; Owner: postgres
--

CREATE TABLE cards.types (
    card text NOT NULL,
    type text NOT NULL
);


ALTER TABLE cards.types OWNER TO postgres;

--
-- Name: entry_card; Type: TABLE; Schema: events; Owner: postgres
--

CREATE TABLE events.entry_card (
    entry_id integer NOT NULL,
    card text NOT NULL,
    mainboard boolean NOT NULL,
    quantity integer NOT NULL,
    CONSTRAINT positive_quantity CHECK ((quantity > 0))
);


ALTER TABLE events.entry_card OWNER TO postgres;

--
-- Name: event_entry; Type: TABLE; Schema: events; Owner: postgres
--

CREATE TABLE events.event_entry (
    tourny_id integer NOT NULL,
    entry_id integer NOT NULL,
    archetype text NOT NULL,
    place text NOT NULL,
    player text NOT NULL,
    deck_name text NOT NULL,
    url text NOT NULL
);


ALTER TABLE events.event_entry OWNER TO postgres;

--
-- Name: event_info; Type: TABLE; Schema: events; Owner: postgres
--

CREATE TABLE events.event_info (
    tourny_id integer NOT NULL,
    name text NOT NULL,
    date date NOT NULL,
    format events.format NOT NULL,
    size integer,
    url text NOT NULL
);


ALTER TABLE events.event_info OWNER TO postgres;

--
-- Name: tournament_entry_entry_id_seq; Type: SEQUENCE; Schema: events; Owner: postgres
--

CREATE SEQUENCE events.tournament_entry_entry_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE events.tournament_entry_entry_id_seq OWNER TO postgres;

--
-- Name: tournament_entry_entry_id_seq; Type: SEQUENCE OWNED BY; Schema: events; Owner: postgres
--

ALTER SEQUENCE events.tournament_entry_entry_id_seq OWNED BY events.event_entry.entry_id;


--
-- Name: tournament_info_tourny_id_seq; Type: SEQUENCE; Schema: events; Owner: postgres
--

CREATE SEQUENCE events.tournament_info_tourny_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE events.tournament_info_tourny_id_seq OWNER TO postgres;

--
-- Name: tournament_info_tourny_id_seq; Type: SEQUENCE OWNED BY; Schema: events; Owner: postgres
--

ALTER SEQUENCE events.tournament_info_tourny_id_seq OWNED BY events.event_info.tourny_id;


--
-- Name: pricing; Type: TABLE; Schema: prices; Owner: postgres
--

CREATE TABLE prices.pricing (
    card text NOT NULL,
    set text NOT NULL,
    date date NOT NULL,
    price money NOT NULL,
    is_paper boolean NOT NULL
);


ALTER TABLE prices.pricing OWNER TO postgres;

--
-- Name: event_entry entry_id; Type: DEFAULT; Schema: events; Owner: postgres
--

ALTER TABLE ONLY events.event_entry ALTER COLUMN entry_id SET DEFAULT nextval('events.tournament_entry_entry_id_seq'::regclass);


--
-- Name: event_info tourny_id; Type: DEFAULT; Schema: events; Owner: postgres
--

ALTER TABLE ONLY events.event_info ALTER COLUMN tourny_id SET DEFAULT nextval('events.tournament_info_tourny_id_seq'::regclass);


--
-- Name: cmc cmc_pkey; Type: CONSTRAINT; Schema: cards; Owner: postgres
--

ALTER TABLE ONLY cards.cmc
    ADD CONSTRAINT cmc_pkey PRIMARY KEY (card);


--
-- Name: colors colors_pkey; Type: CONSTRAINT; Schema: cards; Owner: postgres
--

ALTER TABLE ONLY cards.colors
    ADD CONSTRAINT colors_pkey PRIMARY KEY (card, color);


--
-- Name: printings printings_pkey; Type: CONSTRAINT; Schema: cards; Owner: postgres
--

ALTER TABLE ONLY cards.printings
    ADD CONSTRAINT printings_pkey PRIMARY KEY (card, set);


--
-- Name: pt pt_pkey; Type: CONSTRAINT; Schema: cards; Owner: postgres
--

ALTER TABLE ONLY cards.pt
    ADD CONSTRAINT pt_pkey PRIMARY KEY (card);


--
-- Name: set_info set_info_pkey; Type: CONSTRAINT; Schema: cards; Owner: postgres
--

ALTER TABLE ONLY cards.set_info
    ADD CONSTRAINT set_info_pkey PRIMARY KEY (set);


--
-- Name: text text_pkey; Type: CONSTRAINT; Schema: cards; Owner: postgres
--

ALTER TABLE ONLY cards.text
    ADD CONSTRAINT text_pkey PRIMARY KEY (card);


--
-- Name: types type_pkey; Type: CONSTRAINT; Schema: cards; Owner: postgres
--

ALTER TABLE ONLY cards.types
    ADD CONSTRAINT type_pkey PRIMARY KEY (card, type);


--
-- Name: entry_card entry_card_pkey; Type: CONSTRAINT; Schema: events; Owner: postgres
--

ALTER TABLE ONLY events.entry_card
    ADD CONSTRAINT entry_card_pkey PRIMARY KEY (entry_id, card, mainboard);


--
-- Name: event_entry tournament_entry_pkey; Type: CONSTRAINT; Schema: events; Owner: postgres
--

ALTER TABLE ONLY events.event_entry
    ADD CONSTRAINT tournament_entry_pkey PRIMARY KEY (entry_id);


--
-- Name: event_entry tournament_entry_tourny_id_archetype_place_player_key; Type: CONSTRAINT; Schema: events; Owner: postgres
--

ALTER TABLE ONLY events.event_entry
    ADD CONSTRAINT tournament_entry_tourny_id_archetype_place_player_key UNIQUE (tourny_id, archetype, place, player);


--
-- Name: event_info tournament_info_name_date_format_url_key; Type: CONSTRAINT; Schema: events; Owner: postgres
--

ALTER TABLE ONLY events.event_info
    ADD CONSTRAINT tournament_info_name_date_format_url_key UNIQUE (name, date, format, url);


--
-- Name: event_info tournament_info_pkey; Type: CONSTRAINT; Schema: events; Owner: postgres
--

ALTER TABLE ONLY events.event_info
    ADD CONSTRAINT tournament_info_pkey PRIMARY KEY (tourny_id);


--
-- Name: pricing pricing_unique; Type: CONSTRAINT; Schema: prices; Owner: postgres
--

ALTER TABLE ONLY prices.pricing
    ADD CONSTRAINT pricing_unique UNIQUE (card, set, date, is_paper);


--
-- Name: printings fk_set_info; Type: FK CONSTRAINT; Schema: cards; Owner: postgres
--

ALTER TABLE ONLY cards.printings
    ADD CONSTRAINT fk_set_info FOREIGN KEY (set) REFERENCES cards.set_info(set);


--
-- Name: entry_card entry_card_entry_id_fkey; Type: FK CONSTRAINT; Schema: events; Owner: postgres
--

ALTER TABLE ONLY events.entry_card
    ADD CONSTRAINT entry_card_entry_id_fkey FOREIGN KEY (entry_id) REFERENCES events.event_entry(entry_id);


--
-- Name: event_entry tournament_entry_tourny_id_fkey; Type: FK CONSTRAINT; Schema: events; Owner: postgres
--

ALTER TABLE ONLY events.event_entry
    ADD CONSTRAINT tournament_entry_tourny_id_fkey FOREIGN KEY (tourny_id) REFERENCES events.event_info(tourny_id);


--
-- PostgreSQL database dump complete
--

