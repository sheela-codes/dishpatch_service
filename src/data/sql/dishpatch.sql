--
-- PostgreSQL database dump
--

-- Dumped from database version 14.1
-- Dumped by pg_dump version 14.1

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
-- Name: account_type; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.account_type AS ENUM (
    'Customer',
    'Restaurant',
    'Admin',
    'Driver'
);


ALTER TYPE public.account_type OWNER TO postgres;

--
-- Name: permission_type; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.permission_type AS ENUM (
    'R',
    'RW',
    'RWD',
    'RWDE'
);


ALTER TYPE public.permission_type OWNER TO postgres;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: accounts; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.accounts (
    id integer NOT NULL,
    username text NOT NULL,
    password text NOT NULL,
    permission public.permission_type DEFAULT 'R'::public.permission_type NOT NULL,
    type public.account_type DEFAULT 'Customer'::public.account_type NOT NULL,
    profile_id integer NOT NULL
);


ALTER TABLE public.accounts OWNER TO postgres;

--
-- Name: accounts_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.accounts_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.accounts_id_seq OWNER TO postgres;

--
-- Name: accounts_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.accounts_id_seq OWNED BY public.accounts.id;


--
-- Name: contacts; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.contacts (
    id integer NOT NULL,
    phone_number text NOT NULL,
    email text NOT NULL,
    address text,
    description text
);


ALTER TABLE public.contacts OWNER TO postgres;

--
-- Name: contacts_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.contacts_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.contacts_id_seq OWNER TO postgres;

--
-- Name: contacts_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.contacts_id_seq OWNED BY public.contacts.id;


--
-- Name: deliveries; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.deliveries (
    id integer NOT NULL,
    order_id integer NOT NULL,
    customer_id integer NOT NULL,
    delivery_location text NOT NULL,
    estimated_time timestamp without time zone NOT NULL
);


ALTER TABLE public.deliveries OWNER TO postgres;

--
-- Name: deliveries_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.deliveries_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.deliveries_id_seq OWNER TO postgres;

--
-- Name: deliveries_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.deliveries_id_seq OWNED BY public.deliveries.id;


--
-- Name: menu_items; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.menu_items (
    id integer NOT NULL,
    name text NOT NULL,
    price numeric NOT NULL,
    description text,
    picture text,
    menu_id integer,
    restaurant_id integer NOT NULL
);


ALTER TABLE public.menu_items OWNER TO postgres;

--
-- Name: menu_items_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.menu_items_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.menu_items_id_seq OWNER TO postgres;

--
-- Name: menu_items_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.menu_items_id_seq OWNED BY public.menu_items.id;


--
-- Name: menus; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.menus (
    id integer NOT NULL,
    restaurant_id integer
);


ALTER TABLE public.menus OWNER TO postgres;

--
-- Name: menus_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.menus_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.menus_id_seq OWNER TO postgres;

--
-- Name: menus_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.menus_id_seq OWNED BY public.menus.id;


--
-- Name: orders; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.orders (
    id integer NOT NULL,
    customer_id integer NOT NULL,
    restaurant_id integer NOT NULL,
    driver_id integer
);


ALTER TABLE public.orders OWNER TO postgres;

--
-- Name: orders_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.orders_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.orders_id_seq OWNER TO postgres;

--
-- Name: orders_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.orders_id_seq OWNED BY public.orders.id;


--
-- Name: profiles; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.profiles (
    id integer NOT NULL,
    preferred_name text,
    picture text,
    contact_id integer NOT NULL
);


ALTER TABLE public.profiles OWNER TO postgres;

--
-- Name: profiles_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.profiles_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.profiles_id_seq OWNER TO postgres;

--
-- Name: profiles_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.profiles_id_seq OWNED BY public.profiles.id;


--
-- Name: restaurants; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.restaurants (
    id integer NOT NULL,
    name text NOT NULL,
    operational boolean NOT NULL,
    user_id integer NOT NULL
);


ALTER TABLE public.restaurants OWNER TO postgres;

--
-- Name: restaurants_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.restaurants_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.restaurants_id_seq OWNER TO postgres;

--
-- Name: restaurants_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.restaurants_id_seq OWNED BY public.restaurants.id;


--
-- Name: users; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.users (
    id integer NOT NULL,
    account_id integer NOT NULL
);


ALTER TABLE public.users OWNER TO postgres;

--
-- Name: users_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.users_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.users_id_seq OWNER TO postgres;

--
-- Name: users_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.users_id_seq OWNED BY public.users.id;


--
-- Name: accounts id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.accounts ALTER COLUMN id SET DEFAULT nextval('public.accounts_id_seq'::regclass);


--
-- Name: contacts id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.contacts ALTER COLUMN id SET DEFAULT nextval('public.contacts_id_seq'::regclass);


--
-- Name: deliveries id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.deliveries ALTER COLUMN id SET DEFAULT nextval('public.deliveries_id_seq'::regclass);


--
-- Name: menu_items id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.menu_items ALTER COLUMN id SET DEFAULT nextval('public.menu_items_id_seq'::regclass);


--
-- Name: menus id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.menus ALTER COLUMN id SET DEFAULT nextval('public.menus_id_seq'::regclass);


--
-- Name: orders id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.orders ALTER COLUMN id SET DEFAULT nextval('public.orders_id_seq'::regclass);


--
-- Name: profiles id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.profiles ALTER COLUMN id SET DEFAULT nextval('public.profiles_id_seq'::regclass);


--
-- Name: restaurants id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.restaurants ALTER COLUMN id SET DEFAULT nextval('public.restaurants_id_seq'::regclass);


--
-- Name: users id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users ALTER COLUMN id SET DEFAULT nextval('public.users_id_seq'::regclass);


--
-- Data for Name: accounts; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.accounts (id, username, password, permission, type, profile_id) FROM stdin;
\.


--
-- Data for Name: contacts; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.contacts (id, phone_number, email, address, description) FROM stdin;
\.


--
-- Data for Name: deliveries; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.deliveries (id, order_id, customer_id, delivery_location, estimated_time) FROM stdin;
\.


--
-- Data for Name: menu_items; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.menu_items (id, name, price, description, picture, menu_id, restaurant_id) FROM stdin;
\.


--
-- Data for Name: menus; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.menus (id, restaurant_id) FROM stdin;
\.


--
-- Data for Name: orders; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.orders (id, customer_id, restaurant_id, driver_id) FROM stdin;
\.


--
-- Data for Name: profiles; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.profiles (id, preferred_name, picture, contact_id) FROM stdin;
\.


--
-- Data for Name: restaurants; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.restaurants (id, name, operational, user_id) FROM stdin;
\.


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.users (id, account_id) FROM stdin;
\.


--
-- Name: accounts_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.accounts_id_seq', 1, false);


--
-- Name: contacts_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.contacts_id_seq', 1, false);


--
-- Name: deliveries_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.deliveries_id_seq', 1, false);


--
-- Name: menu_items_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.menu_items_id_seq', 1, false);


--
-- Name: menus_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.menus_id_seq', 1, false);


--
-- Name: orders_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.orders_id_seq', 1, false);


--
-- Name: profiles_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.profiles_id_seq', 1, false);


--
-- Name: restaurants_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.restaurants_id_seq', 1, false);


--
-- Name: users_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.users_id_seq', 1, false);


--
-- Name: accounts accounts_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.accounts
    ADD CONSTRAINT accounts_pkey PRIMARY KEY (id);


--
-- Name: accounts accounts_username_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.accounts
    ADD CONSTRAINT accounts_username_key UNIQUE (username);


--
-- Name: contacts contacts_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.contacts
    ADD CONSTRAINT contacts_pkey PRIMARY KEY (id);


--
-- Name: deliveries deliveries_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.deliveries
    ADD CONSTRAINT deliveries_pkey PRIMARY KEY (id);


--
-- Name: menu_items menu_items_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.menu_items
    ADD CONSTRAINT menu_items_pkey PRIMARY KEY (id);


--
-- Name: menus menus_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.menus
    ADD CONSTRAINT menus_pkey PRIMARY KEY (id);


--
-- Name: orders orders_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.orders
    ADD CONSTRAINT orders_pkey PRIMARY KEY (id);


--
-- Name: profiles profiles_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.profiles
    ADD CONSTRAINT profiles_pkey PRIMARY KEY (id);


--
-- Name: restaurants restaurants_name_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.restaurants
    ADD CONSTRAINT restaurants_name_key UNIQUE (name);


--
-- Name: restaurants restaurants_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.restaurants
    ADD CONSTRAINT restaurants_pkey PRIMARY KEY (id);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: accounts fk_account_profile; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.accounts
    ADD CONSTRAINT fk_account_profile FOREIGN KEY (profile_id) REFERENCES public.profiles(id);


--
-- Name: profiles fk_employee_contact_info; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.profiles
    ADD CONSTRAINT fk_employee_contact_info FOREIGN KEY (contact_id) REFERENCES public.contacts(id);


--
-- Name: menu_items fk_menus_menu_item; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.menu_items
    ADD CONSTRAINT fk_menus_menu_item FOREIGN KEY (menu_id) REFERENCES public.menus(id);


--
-- Name: orders fk_order_customer; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.orders
    ADD CONSTRAINT fk_order_customer FOREIGN KEY (customer_id) REFERENCES public.users(id);


--
-- Name: orders fk_order_driver; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.orders
    ADD CONSTRAINT fk_order_driver FOREIGN KEY (driver_id) REFERENCES public.users(id);


--
-- Name: orders fk_order_restaurant; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.orders
    ADD CONSTRAINT fk_order_restaurant FOREIGN KEY (restaurant_id) REFERENCES public.restaurants(id);


--
-- Name: restaurants fk_restaurant_account; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.restaurants
    ADD CONSTRAINT fk_restaurant_account FOREIGN KEY (user_id) REFERENCES public.users(id);



--
-- Name: menu_items fk_restaurant_menu_item; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.menu_items
    ADD CONSTRAINT fk_restaurant_menu_item FOREIGN KEY (restaurant_id) REFERENCES public.restaurants(id);


--
-- Name: users fk_user_account; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT fk_user_account FOREIGN KEY (account_id) REFERENCES public.accounts(id);

-- many to many relationship between orders and one menu_item, order can have many menu items and a menu_item can be in many orders.
CREATE TABLE public.order_items (
    order_id     integer NOT NULL,
    menu_item_id integer NOT NULL,
    quantity     integer NOT NULL CHECK (quantity > 0),
    unit_price   numeric(10,2) NOT NULL,  -- price at time of order
    PRIMARY KEY (order_id, menu_item_id)
);    

ALTER TABLE public.order_items
    ADD CONSTRAINT fk_order_order_item FOREIGN KEY (order_id) REFERENCES public.orders(id),
    ADD CONSTRAINT fk_order_item_menu_item FOREIGN KEY (menu_item_id) REFERENCES public.menu_items(id); 


--
-- PostgreSQL database dump complete
--

-- =====================================================================
-- Round 1 enrichment: order lifecycle, cuisines, restaurant details
-- =====================================================================

-- Order lifecycle ------------------------------------------------------

CREATE TYPE public.order_status AS ENUM (
    'placed',
    'accepted',
    'preparing',
    'picked_up',
    'delivered',
    'cancelled'
);

ALTER TABLE public.orders
    ADD COLUMN status       public.order_status NOT NULL DEFAULT 'placed',
    ADD COLUMN placed_at    timestamptz NOT NULL DEFAULT now(),
    ADD COLUMN accepted_at  timestamptz,   -- restaurant accepts the order
    ADD COLUMN picked_up_at timestamptz,   -- driver collects the food
    ADD COLUMN delivered_at timestamptz,   -- food reaches the customer
    ADD COLUMN cancelled_at timestamptz,
    -- each step can only happen after the one before it
    ADD CONSTRAINT orders_timeline_check CHECK (
        (accepted_at  IS NULL OR accepted_at  >= placed_at)    AND
        (picked_up_at IS NULL OR picked_up_at >= accepted_at)  AND
        (delivered_at IS NULL OR delivered_at >= picked_up_at)
    );

-- Cuisines ---------------------------------------------------------------

CREATE TABLE public.cuisines (
    id   integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name text NOT NULL UNIQUE
);

INSERT INTO public.cuisines (name) VALUES
    ('American'), ('Chinese'), ('Indian'), ('Italian'),
    ('Japanese'), ('Mediterranean'), ('Mexican'), ('Thai');

-- Restaurant details -----------------------------------------------------

ALTER TABLE public.restaurants
    ADD COLUMN cuisine_id integer NOT NULL REFERENCES public.cuisines(id),
    ADD COLUMN city       text NOT NULL,
    ADD COLUMN opened_at  date;


-- =====================================================================
-- Round 2: partner data loading (see requirements/ingester.md, section 9)
-- =====================================================================

-- Partner IDs. UNIQUE stops the same partner record being loaded twice
-- (NULL is allowed: records created directly on Dishpatch have no partner ref).
ALTER TABLE public.restaurants ADD COLUMN external_ref text UNIQUE;   -- 'R007'
ALTER TABLE public.menu_items  ADD COLUMN external_ref text UNIQUE;   -- 'M0071'
ALTER TABLE public.users       ADD COLUMN external_ref text UNIQUE;   -- 'C0042', 'D003'
ALTER TABLE public.orders      ADD COLUMN external_ref text UNIQUE;   -- 'O-20261019-0013'

-- Soft delete: switched off, never deleted (old orders still point at them).
ALTER TABLE public.menu_items ADD COLUMN active boolean NOT NULL DEFAULT true;
ALTER TABLE public.users      ADD COLUMN active boolean NOT NULL DEFAULT true;

-- Details the partner sends that had no column yet.
ALTER TABLE public.contacts ADD COLUMN city text;
ALTER TABLE public.users    ADD COLUMN created_at timestamptz;          -- customer signed_up_at

-- Load log: which partner files have been loaded, so re-runs skip them.
CREATE TABLE public.file_loads (
    folder        text NOT NULL,                       -- '2026/10/19'
    file_name     text NOT NULL,                       -- 'activity/orders.jsonl'
    checksum      text NOT NULL,                       -- SHA-256 of the file
    rows_loaded   integer NOT NULL,
    rows_rejected integer NOT NULL,
    loaded_at     timestamptz NOT NULL DEFAULT now(),
    PRIMARY KEY (folder, file_name)
);

CREATE INDEX idx_orders_customer_id   ON public.orders (customer_id);
CREATE INDEX idx_orders_restaurant_id ON public.orders (restaurant_id);
