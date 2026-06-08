--
-- PostgreSQL database dump
--

\restrict sdvWXDvMPbAyf1oUA0lP09YuW2p8GGh3uFQa9PPkCcy6p9OlN26ADts3nlBCTH2

-- Dumped from database version 17.10
-- Dumped by pg_dump version 17.10

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: admin_logs; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.admin_logs (
    id integer NOT NULL,
    admin_id integer NOT NULL,
    action character varying(100) NOT NULL,
    description text,
    created_at timestamp without time zone
);


ALTER TABLE public.admin_logs OWNER TO postgres;

--
-- Name: admin_logs_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.admin_logs_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.admin_logs_id_seq OWNER TO postgres;

--
-- Name: admin_logs_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.admin_logs_id_seq OWNED BY public.admin_logs.id;


--
-- Name: alembic_version; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.alembic_version (
    version_num character varying(32) NOT NULL
);


ALTER TABLE public.alembic_version OWNER TO postgres;

--
-- Name: amenities; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.amenities (
    id integer NOT NULL,
    amenity_name character varying(100) NOT NULL
);


ALTER TABLE public.amenities OWNER TO postgres;

--
-- Name: amenities_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.amenities_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.amenities_id_seq OWNER TO postgres;

--
-- Name: amenities_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.amenities_id_seq OWNED BY public.amenities.id;


--
-- Name: chats; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.chats (
    id integer NOT NULL,
    sender_id integer NOT NULL,
    receiver_id integer NOT NULL,
    property_id integer,
    message text NOT NULL,
    sent_at timestamp without time zone
);


ALTER TABLE public.chats OWNER TO postgres;

--
-- Name: chats_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.chats_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.chats_id_seq OWNER TO postgres;

--
-- Name: chats_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.chats_id_seq OWNED BY public.chats.id;


--
-- Name: favorites; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.favorites (
    id integer NOT NULL,
    user_id integer NOT NULL,
    property_id integer NOT NULL,
    created_at timestamp without time zone
);


ALTER TABLE public.favorites OWNER TO postgres;

--
-- Name: favorites_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.favorites_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.favorites_id_seq OWNER TO postgres;

--
-- Name: favorites_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.favorites_id_seq OWNED BY public.favorites.id;


--
-- Name: owner_profiles; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.owner_profiles (
    id integer NOT NULL,
    user_id integer NOT NULL,
    citizenship_number character varying(50),
    citizenship_front_image character varying(256),
    citizenship_back_image character varying(256),
    owner_type character varying(50),
    verification_status character varying(20),
    created_at timestamp without time zone,
    updated_at timestamp without time zone
);


ALTER TABLE public.owner_profiles OWNER TO postgres;

--
-- Name: owner_profiles_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.owner_profiles_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.owner_profiles_id_seq OWNER TO postgres;

--
-- Name: owner_profiles_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.owner_profiles_id_seq OWNED BY public.owner_profiles.id;


--
-- Name: properties; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.properties (
    id integer NOT NULL,
    owner_id integer NOT NULL,
    title character varying(200) NOT NULL,
    description text,
    property_type character varying(50) NOT NULL,
    price numeric(10,2) NOT NULL,
    province character varying(100),
    district character varying(100),
    city character varying(100) NOT NULL,
    area character varying(100),
    address text,
    latitude double precision,
    longitude double precision,
    bedrooms integer,
    bathrooms integer,
    furnished boolean,
    parking boolean,
    availability_status character varying(20),
    verification_status character varying(20),
    status character varying(20),
    created_at timestamp without time zone,
    updated_at timestamp without time zone
);


ALTER TABLE public.properties OWNER TO postgres;

--
-- Name: properties_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.properties_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.properties_id_seq OWNER TO postgres;

--
-- Name: properties_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.properties_id_seq OWNED BY public.properties.id;


--
-- Name: property_amenities; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.property_amenities (
    id integer NOT NULL,
    property_id integer NOT NULL,
    amenity_id integer NOT NULL
);


ALTER TABLE public.property_amenities OWNER TO postgres;

--
-- Name: property_amenities_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.property_amenities_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.property_amenities_id_seq OWNER TO postgres;

--
-- Name: property_amenities_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.property_amenities_id_seq OWNED BY public.property_amenities.id;


--
-- Name: property_documents; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.property_documents (
    id integer NOT NULL,
    property_id integer NOT NULL,
    document_type character varying(50),
    document_file character varying(256) NOT NULL,
    verification_status character varying(20),
    created_at timestamp without time zone
);


ALTER TABLE public.property_documents OWNER TO postgres;

--
-- Name: property_documents_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.property_documents_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.property_documents_id_seq OWNER TO postgres;

--
-- Name: property_documents_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.property_documents_id_seq OWNED BY public.property_documents.id;


--
-- Name: property_images; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.property_images (
    id integer NOT NULL,
    property_id integer NOT NULL,
    image_path character varying(256) NOT NULL,
    created_at timestamp without time zone
);


ALTER TABLE public.property_images OWNER TO postgres;

--
-- Name: property_images_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.property_images_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.property_images_id_seq OWNER TO postgres;

--
-- Name: property_images_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.property_images_id_seq OWNED BY public.property_images.id;


--
-- Name: reports; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.reports (
    id integer NOT NULL,
    reported_by integer NOT NULL,
    property_id integer NOT NULL,
    reason text NOT NULL,
    status character varying(20),
    created_at timestamp without time zone
);


ALTER TABLE public.reports OWNER TO postgres;

--
-- Name: reports_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.reports_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.reports_id_seq OWNER TO postgres;

--
-- Name: reports_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.reports_id_seq OWNED BY public.reports.id;


--
-- Name: reviews; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.reviews (
    id integer NOT NULL,
    property_id integer NOT NULL,
    user_id integer NOT NULL,
    rating integer NOT NULL,
    review text,
    created_at timestamp without time zone
);


ALTER TABLE public.reviews OWNER TO postgres;

--
-- Name: reviews_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.reviews_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.reviews_id_seq OWNER TO postgres;

--
-- Name: reviews_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.reviews_id_seq OWNED BY public.reviews.id;


--
-- Name: roommate_profiles; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.roommate_profiles (
    id integer NOT NULL,
    user_id integer NOT NULL,
    preferred_city character varying(100),
    budget numeric(10,2),
    occupation character varying(100),
    gender_preference character varying(20),
    smoking_preference character varying(20),
    drinking_preference character varying(20),
    lifestyle text,
    bio text,
    created_at timestamp without time zone
);


ALTER TABLE public.roommate_profiles OWNER TO postgres;

--
-- Name: roommate_profiles_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.roommate_profiles_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.roommate_profiles_id_seq OWNER TO postgres;

--
-- Name: roommate_profiles_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.roommate_profiles_id_seq OWNED BY public.roommate_profiles.id;


--
-- Name: users; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.users (
    id integer NOT NULL,
    full_name character varying(150) NOT NULL,
    email character varying(150) NOT NULL,
    phone character varying(20),
    password character varying(256) NOT NULL,
    role character varying(20) NOT NULL,
    gender character varying(20),
    occupation character varying(100),
    profile_image character varying(256),
    province character varying(100),
    district character varying(100),
    city character varying(100),
    address text,
    account_status character varying(20) NOT NULL,
    created_at timestamp without time zone,
    updated_at timestamp without time zone,
    profile_complete boolean DEFAULT false NOT NULL
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


ALTER SEQUENCE public.users_id_seq OWNER TO postgres;

--
-- Name: users_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.users_id_seq OWNED BY public.users.id;


--
-- Name: vacancy_calendar; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.vacancy_calendar (
    id integer NOT NULL,
    property_id integer NOT NULL,
    available_from date NOT NULL,
    available_until date,
    status character varying(20)
);


ALTER TABLE public.vacancy_calendar OWNER TO postgres;

--
-- Name: vacancy_calendar_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.vacancy_calendar_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.vacancy_calendar_id_seq OWNER TO postgres;

--
-- Name: vacancy_calendar_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.vacancy_calendar_id_seq OWNED BY public.vacancy_calendar.id;


--
-- Name: admin_logs id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.admin_logs ALTER COLUMN id SET DEFAULT nextval('public.admin_logs_id_seq'::regclass);


--
-- Name: amenities id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.amenities ALTER COLUMN id SET DEFAULT nextval('public.amenities_id_seq'::regclass);


--
-- Name: chats id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.chats ALTER COLUMN id SET DEFAULT nextval('public.chats_id_seq'::regclass);


--
-- Name: favorites id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.favorites ALTER COLUMN id SET DEFAULT nextval('public.favorites_id_seq'::regclass);


--
-- Name: owner_profiles id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.owner_profiles ALTER COLUMN id SET DEFAULT nextval('public.owner_profiles_id_seq'::regclass);


--
-- Name: properties id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.properties ALTER COLUMN id SET DEFAULT nextval('public.properties_id_seq'::regclass);


--
-- Name: property_amenities id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.property_amenities ALTER COLUMN id SET DEFAULT nextval('public.property_amenities_id_seq'::regclass);


--
-- Name: property_documents id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.property_documents ALTER COLUMN id SET DEFAULT nextval('public.property_documents_id_seq'::regclass);


--
-- Name: property_images id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.property_images ALTER COLUMN id SET DEFAULT nextval('public.property_images_id_seq'::regclass);


--
-- Name: reports id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.reports ALTER COLUMN id SET DEFAULT nextval('public.reports_id_seq'::regclass);


--
-- Name: reviews id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.reviews ALTER COLUMN id SET DEFAULT nextval('public.reviews_id_seq'::regclass);


--
-- Name: roommate_profiles id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.roommate_profiles ALTER COLUMN id SET DEFAULT nextval('public.roommate_profiles_id_seq'::regclass);


--
-- Name: users id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users ALTER COLUMN id SET DEFAULT nextval('public.users_id_seq'::regclass);


--
-- Name: vacancy_calendar id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.vacancy_calendar ALTER COLUMN id SET DEFAULT nextval('public.vacancy_calendar_id_seq'::regclass);


--
-- Data for Name: admin_logs; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.admin_logs (id, admin_id, action, description, created_at) FROM stdin;
\.


--
-- Data for Name: alembic_version; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.alembic_version (version_num) FROM stdin;
1a5171be7e16
\.


--
-- Data for Name: amenities; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.amenities (id, amenity_name) FROM stdin;
1	WiFi
2	Water Supply
3	Electricity Backup
4	Generator
5	Parking
6	Lift/Elevator
7	Security Guard
8	CCTV
9	Air Conditioning
10	Balcony
11	Garden
12	Gym
13	Laundry
14	Kitchen
15	Refrigerator
16	Washing Machine
17	Cable TV
18	Solar Power
19	Water Heater
20	Swimming Pool
\.


--
-- Data for Name: chats; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.chats (id, sender_id, receiver_id, property_id, message, sent_at) FROM stdin;
1	10	9	32	Can you please confirm if utilities like water and electricity are included?	2026-05-07 04:43:06.578558
2	10	6	20	Hi, could you please share more details about the monthly rent and advance?	2026-06-04 04:43:06.578558
3	11	3	8	Can you please confirm if utilities like water and electricity are included?	2026-05-09 04:43:06.578558
4	11	5	17	Hello, I am interested in renting this property. Is it still available?	2026-05-08 04:43:06.578558
5	12	4	9	Is the price negotiable? I am looking for long-term rent.	2026-05-29 04:43:06.578558
6	12	5	16	Hi, could you please share more details about the monthly rent and advance?	2026-05-26 04:43:06.578558
7	13	4	10	Good day! I would like to schedule a visit. When are you available?	2026-05-21 04:43:06.578558
8	13	3	8	Hi, could you please share more details about the monthly rent and advance?	2026-05-30 04:43:06.578558
9	14	6	20	Can you please confirm if utilities like water and electricity are included?	2026-05-25 04:43:06.578558
10	14	2	2	Is the price negotiable? I am looking for long-term rent.	2026-05-21 04:43:06.578558
11	15	6	21	Hello, I am interested in renting this property. Is it still available?	2026-05-06 04:43:06.578558
12	15	4	13	Can you please confirm if utilities like water and electricity are included?	2026-05-26 04:43:06.578558
13	16	9	34	Hi, could you please share more details about the monthly rent and advance?	2026-05-09 04:43:06.579584
14	16	9	35	Can you please confirm if utilities like water and electricity are included?	2026-05-22 04:43:06.579584
15	17	9	32	Hi, could you please share more details about the monthly rent and advance?	2026-05-30 04:43:06.579584
16	17	4	9	Hi, could you please share more details about the monthly rent and advance?	2026-05-07 04:43:06.579584
17	18	3	7	Hi, could you please share more details about the monthly rent and advance?	2026-05-14 04:43:06.579584
18	18	9	32	Good day! I would like to schedule a visit. When are you available?	2026-05-16 04:43:06.579584
19	19	4	10	Hello, I am interested in renting this property. Is it still available?	2026-05-26 04:43:06.579584
20	19	7	24	Good day! I would like to schedule a visit. When are you available?	2026-05-07 04:43:06.579584
\.


--
-- Data for Name: favorites; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.favorites (id, user_id, property_id, created_at) FROM stdin;
1	10	35	2026-05-30 04:43:06.578558
2	10	34	2026-04-09 04:43:06.578558
3	10	6	2026-05-27 04:43:06.578558
4	11	14	2026-05-10 04:43:06.578558
5	11	34	2026-04-07 04:43:06.578558
6	11	20	2026-05-28 04:43:06.578558
7	12	14	2026-05-24 04:43:06.578558
8	12	25	2026-04-23 04:43:06.578558
9	13	23	2026-06-02 04:43:06.578558
10	13	12	2026-04-08 04:43:06.578558
11	13	14	2026-04-15 04:43:06.578558
12	14	27	2026-04-13 04:43:06.578558
13	14	11	2026-04-24 04:43:06.578558
14	14	13	2026-05-18 04:43:06.578558
15	15	9	2026-04-15 04:43:06.578558
16	15	24	2026-05-23 04:43:06.578558
17	16	23	2026-04-24 04:43:06.578558
18	16	5	2026-05-24 04:43:06.578558
19	17	19	2026-05-12 04:43:06.579584
20	17	15	2026-04-18 04:43:06.579584
21	18	12	2026-05-07 04:43:06.579584
22	18	21	2026-04-22 04:43:06.579584
23	18	8	2026-05-22 04:43:06.579584
24	19	1	2026-04-16 04:43:06.579584
25	19	9	2026-05-12 04:43:06.579584
26	19	27	2026-04-28 04:43:06.579584
27	19	14	2026-04-27 04:43:06.579584
\.


--
-- Data for Name: owner_profiles; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.owner_profiles (id, user_id, citizenship_number, citizenship_front_image, citizenship_back_image, owner_type, verification_status, created_at, updated_at) FROM stdin;
1	2	04075918	\N	\N	agency	verified	2026-06-05 04:43:05.328173	2026-06-05 04:43:05.328173
2	3	04027201	\N	\N	individual	verified	2026-06-05 04:43:05.417908	2026-06-05 04:43:05.417908
3	4	04024480	\N	\N	agency	verified	2026-06-05 04:43:05.496665	2026-06-05 04:43:05.496665
4	5	04090983	\N	\N	agency	verified	2026-06-05 04:43:05.584398	2026-06-05 04:43:05.584398
5	6	04070381	\N	\N	individual	verified	2026-06-05 04:43:05.663965	2026-06-05 04:43:05.663965
6	7	04038713	\N	\N	individual	verified	2026-06-05 04:43:05.736015	2026-06-05 04:43:05.736015
7	8	04095626	\N	\N	individual	pending	2026-06-05 04:43:05.810953	2026-06-05 04:43:05.810953
8	9	04015563	\N	\N	individual	pending	2026-06-05 04:43:05.891971	2026-06-05 04:43:05.891971
\.


--
-- Data for Name: properties; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.properties (id, owner_id, title, description, property_type, price, province, district, city, area, address, latitude, longitude, bedrooms, bathrooms, furnished, parking, availability_status, verification_status, status, created_at, updated_at) FROM stdin;
1	2	Budget Room in Kalikanagar	Well-maintained property with excellent ventilation and natural light. Located in a quiet neighborhood with easy access to public transport, markets, and schools. Ideal for families and working professionals.	room	4000.00	Lumbini	Rupandehi	Butwal	Kalikanagar	Kalikanagar, Butwal, Nepal	27.705183	83.453386	1	1	f	f	available	verified	active	2026-04-25 04:43:05.327168	2026-06-05 04:43:05.331166
2	2	New 2BHK Apartment in Tikapur	Recently renovated property featuring modern interiors and quality fittings. The location offers great connectivity to the city center. Water supply and electricity backup available.	apartment	14500.00	Sudurpashchim	Kailali	Dhangadhi	Tikapur	Tikapur, Dhangadhi, Nepal	28.699269	80.611589	2	2	t	f	available	verified	active	2026-02-11 04:43:05.339169	2026-06-05 04:43:05.34018
3	2	Cozy Single Room near Chabahil	Strategically located property with excellent road connectivity. Suitable for both residential and small commercial purposes. Owner is cooperative and responsive.	room	8000.00	Bagmati	Kathmandu	Kathmandu	Chabahil	Chabahil, Kathmandu, Nepal	27.728846	85.307515	1	1	f	f	available	verified	active	2026-04-02 04:43:05.344168	2026-06-05 04:43:05.344168
4	2	2BHK Flat near Ghantaghar	Beautiful property in a prime location. High-speed internet connectivity available. Proximity to major offices and commercial areas makes this an ideal choice for professionals.	flat	12500.00	Koshi	Morang	Biratnagar	Ghantaghar	Ghantaghar, Biratnagar, Nepal	26.441128	87.278593	2	1	t	f	available	verified	active	2026-03-15 04:43:05.348168	2026-06-05 04:43:05.349166
5	3	Modern 2BHK Flat in B.P. Chowk	Well-maintained property with excellent ventilation and natural light. Located in a quiet neighborhood with easy access to public transport, markets, and schools. Ideal for families and working professionals.	flat	21000.00	Koshi	Sunsari	Dharan	B.P. Chowk	B.P. Chowk, Dharan, Nepal	26.814901	87.291572	2	1	t	f	available	verified	active	2026-01-22 04:43:05.417908	2026-06-05 04:43:05.41896
6	3	Office Space in Dhangadhi-4	Well-maintained property with excellent ventilation and natural light. Located in a quiet neighborhood with easy access to public transport, markets, and schools. Ideal for families and working professionals.	shutter	48500.00	Sudurpashchim	Kailali	Dhangadhi	Dhangadhi-4	Dhangadhi-4, Dhangadhi, Nepal	28.68848	80.587711	0	1	f	f	available	verified	active	2025-12-25 04:43:05.41896	2026-06-05 04:43:05.41896
7	3	2BHK Flat near Bharatpur-11	Recently renovated property featuring modern interiors and quality fittings. The location offers great connectivity to the city center. Water supply and electricity backup available.	flat	10000.00	Bagmati	Chitwan	Chitwan	Bharatpur-11	Bharatpur-11, Chitwan, Nepal	27.543887	84.371773	2	1	t	f	available	verified	active	2025-12-23 04:43:05.423908	2026-06-05 04:43:05.423908
8	3	Affordable Room in Kailali	Well-maintained property with excellent ventilation and natural light. Located in a quiet neighborhood with easy access to public transport, markets, and schools. Ideal for families and working professionals.	room	5500.00	Sudurpashchim	Kailali	Dhangadhi	Kailali	Kailali, Dhangadhi, Nepal	28.712249	80.612945	1	1	f	t	available	verified	active	2026-01-15 04:43:05.426906	2026-06-05 04:43:05.427906
9	4	Luxury Apartment in B.P. Chowk	Beautiful property in a prime location. High-speed internet connectivity available. Proximity to major offices and commercial areas makes this an ideal choice for professionals.	apartment	46000.00	Koshi	Sunsari	Dharan	B.P. Chowk	B.P. Chowk, Dharan, Nepal	26.806314	87.295761	3	2	t	f	available	verified	active	2026-04-17 04:43:05.496665	2026-06-05 04:43:05.497683
10	4	New 2BHK Apartment in Ratnanagar	Spacious and airy property perfect for a small family or working professionals. Close to hospitals, schools, and shopping centers. 24/7 security with CCTV surveillance.	apartment	25500.00	Bagmati	Chitwan	Chitwan	Ratnanagar	Ratnanagar, Chitwan, Nepal	27.531552	84.334904	2	2	t	f	available	verified	active	2026-02-20 04:43:05.497683	2026-06-05 04:43:05.498663
11	4	Furnished Studio in Khairahani	Clean and comfortable property at an affordable price. The neighborhood is safe and friendly. All essential amenities within walking distance.	flat	8500.00	Bagmati	Chitwan	Chitwan	Khairahani	Khairahani, Chitwan, Nepal	27.543996	84.358259	1	1	t	f	available	verified	active	2026-04-09 04:43:05.502668	2026-06-05 04:43:05.502668
12	4	Spacious 3BHK House in Pulchowk	Recently renovated property featuring modern interiors and quality fittings. The location offers great connectivity to the city center. Water supply and electricity backup available.	house	47000.00	Bagmati	Lalitpur	Lalitpur	Pulchowk	Pulchowk, Lalitpur, Nepal	27.660875	85.327298	3	2	t	f	available	verified	active	2026-02-22 04:43:05.503668	2026-06-05 04:43:05.50462
13	4	Cozy Single Room near Thamel	Beautiful property in a prime location. High-speed internet connectivity available. Proximity to major offices and commercial areas makes this an ideal choice for professionals.	room	4000.00	Bagmati	Kathmandu	Kathmandu	Thamel	Thamel, Kathmandu, Nepal	27.712155	85.32553	1	1	f	f	available	verified	active	2026-04-24 04:43:05.506663	2026-06-05 04:43:05.507668
14	5	4BHK Bungalow in Traffic Chowk	Cozy and well-furnished property perfect for students and young professionals. Nearby restaurants, cafes, and entertainment options. Flexible lease terms available.	house	63000.00	Lumbini	Rupandehi	Butwal	Traffic Chowk	Traffic Chowk, Butwal, Nepal	27.70088	83.447822	4	3	t	f	available	verified	active	2026-01-25 04:43:05.584398	2026-06-05 04:43:05.584398
15	5	Luxury Apartment in Imadol	Strategically located property with excellent road connectivity. Suitable for both residential and small commercial purposes. Owner is cooperative and responsive.	apartment	36500.00	Bagmati	Lalitpur	Lalitpur	Imadol	Imadol, Lalitpur, Nepal	27.655246	85.311502	3	2	t	t	available	verified	active	2025-12-27 04:43:05.585401	2026-06-05 04:43:05.585401
16	5	Commercial Shutter in Buddhanagar	Well-maintained property with excellent ventilation and natural light. Located in a quiet neighborhood with easy access to public transport, markets, and schools. Ideal for families and working professionals.	shutter	11000.00	Koshi	Morang	Biratnagar	Buddhanagar	Buddhanagar, Biratnagar, Nepal	26.43258	87.275447	0	1	f	t	available	verified	active	2026-02-09 04:43:05.586398	2026-06-05 04:43:05.5874
17	5	New 2BHK Apartment in Imadol	Spacious and airy property perfect for a small family or working professionals. Close to hospitals, schools, and shopping centers. 24/7 security with CCTV surveillance.	apartment	20500.00	Bagmati	Lalitpur	Lalitpur	Imadol	Imadol, Lalitpur, Nepal	27.665326	85.317598	2	2	t	t	available	verified	active	2026-03-26 04:43:05.588399	2026-06-05 04:43:05.588399
18	5	Office Space in Dhangadhi-4	Recently renovated property featuring modern interiors and quality fittings. The location offers great connectivity to the city center. Water supply and electricity backup available.	shutter	28500.00	Sudurpashchim	Kailali	Dhangadhi	Dhangadhi-4	Dhangadhi-4, Dhangadhi, Nepal	28.695444	80.599285	0	1	f	t	available	verified	active	2026-05-26 04:43:05.590919	2026-06-05 04:43:05.591939
19	6	4BHK Bungalow in Vijaypur	Clean and comfortable property at an affordable price. The neighborhood is safe and friendly. All essential amenities within walking distance.	house	58000.00	Koshi	Sunsari	Dharan	Vijaypur	Vijaypur, Dharan, Nepal	26.802742	87.286378	4	3	t	f	available	verified	active	2026-01-13 04:43:05.662959	2026-06-05 04:43:05.663965
20	6	Spacious 3BHK House in Bhedetar	Clean and comfortable property at an affordable price. The neighborhood is safe and friendly. All essential amenities within walking distance.	house	42000.00	Koshi	Sunsari	Dharan	Bhedetar	Bhedetar, Dharan, Nepal	26.816836	87.290422	3	2	t	t	available	verified	active	2026-03-29 04:43:05.664955	2026-06-05 04:43:05.664955
21	6	Luxury Apartment in Bagar	Beautiful property in a prime location. High-speed internet connectivity available. Proximity to major offices and commercial areas makes this an ideal choice for professionals.	apartment	27500.00	Gandaki	Kaski	Pokhara	Bagar	Bagar, Pokhara, Nepal	28.212497	83.974614	3	2	t	f	available	verified	active	2026-02-02 04:43:05.666034	2026-06-05 04:43:05.667029
22	7	Cozy Single Room near Jahada	Clean and comfortable property at an affordable price. The neighborhood is safe and friendly. All essential amenities within walking distance.	room	8000.00	Koshi	Morang	Biratnagar	Jahada	Jahada, Biratnagar, Nepal	26.468661	87.290451	1	1	f	f	available	verified	active	2026-04-30 04:43:05.736015	2026-06-05 04:43:05.736015
23	7	Commercial Shutter in Rambazar	Strategically located property with excellent road connectivity. Suitable for both residential and small commercial purposes. Owner is cooperative and responsive.	shutter	19000.00	Gandaki	Kaski	Pokhara	Rambazar	Rambazar, Pokhara, Nepal	28.192911	84.002996	0	1	f	f	available	verified	active	2025-12-14 04:43:05.737072	2026-06-05 04:43:05.737072
24	7	2BHK Flat near Ghantaghar	Spacious and airy property perfect for a small family or working professionals. Close to hospitals, schools, and shopping centers. 24/7 security with CCTV surveillance.	flat	20000.00	Madhesh	Parsa	Birgunj	Ghantaghar	Ghantaghar, Birgunj, Nepal	27.002029	84.873112	2	1	t	f	available	verified	active	2026-03-30 04:43:05.738084	2026-06-05 04:43:05.739082
25	7	4BHK Bungalow in Bharatpur-10	Beautiful property in a prime location. High-speed internet connectivity available. Proximity to major offices and commercial areas makes this an ideal choice for professionals.	house	80000.00	Bagmati	Chitwan	Chitwan	Bharatpur-10	Bharatpur-10, Chitwan, Nepal	27.51078	84.345711	4	3	t	f	available	verified	active	2026-01-09 04:43:05.740079	2026-06-05 04:43:05.740079
26	7	Furnished Studio in Suryabinayak	Clean and comfortable property at an affordable price. The neighborhood is safe and friendly. All essential amenities within walking distance.	flat	14000.00	Bagmati	Bhaktapur	Bhaktapur	Suryabinayak	Suryabinayak, Bhaktapur, Nepal	27.667262	85.444518	1	1	t	f	available	verified	active	2026-03-27 04:43:05.742024	2026-06-05 04:43:05.742024
27	8	Student Hostel near Satdobato	Well-maintained property with excellent ventilation and natural light. Located in a quiet neighborhood with easy access to public transport, markets, and schools. Ideal for families and working professionals.	hostel	4500.00	Bagmati	Lalitpur	Lalitpur	Satdobato	Satdobato, Lalitpur, Nepal	27.662636	85.327312	1	1	f	t	available	verified	active	2025-12-24 04:43:05.80997	2026-06-05 04:43:05.810953
28	8	2BHK Flat near Ghantaghar	Strategically located property with excellent road connectivity. Suitable for both residential and small commercial purposes. Owner is cooperative and responsive.	flat	17000.00	Madhesh	Parsa	Birgunj	Ghantaghar	Ghantaghar, Birgunj, Nepal	26.996863	84.872621	2	1	t	t	available	pending	active	2026-03-03 04:43:05.810953	2026-06-05 04:43:05.81197
29	8	Affordable Room in Lakeside	Strategically located property with excellent road connectivity. Suitable for both residential and small commercial purposes. Owner is cooperative and responsive.	room	6000.00	Gandaki	Kaski	Pokhara	Lakeside	Lakeside, Pokhara, Nepal	28.217625	83.973092	1	1	f	t	available	pending	active	2026-03-28 04:43:05.81297	2026-06-05 04:43:05.81297
30	8	Cozy Single Room near Katunje	Premium property with modern amenities including parking, elevator, and generator backup. The property is in excellent condition and ready to move in.	room	8000.00	Bagmati	Bhaktapur	Bhaktapur	Katunje	Katunje, Bhaktapur, Nepal	27.688111	85.411615	1	1	f	f	available	verified	active	2026-04-15 04:43:05.814969	2026-06-05 04:43:05.814969
31	8	Commercial Shutter in Milanchowk	Spacious and airy property perfect for a small family or working professionals. Close to hospitals, schools, and shopping centers. 24/7 security with CCTV surveillance.	shutter	30000.00	Lumbini	Rupandehi	Butwal	Milanchowk	Milanchowk, Butwal, Nepal	27.69696	83.447459	0	1	f	f	available	pending	active	2026-05-10 04:43:05.815968	2026-06-05 04:43:05.81696
32	9	Office Space in Tikapur	Premium property with modern amenities including parking, elevator, and generator backup. The property is in excellent condition and ready to move in.	shutter	19000.00	Sudurpashchim	Kailali	Dhangadhi	Tikapur	Tikapur, Dhangadhi, Nepal	28.675751	80.603045	0	1	f	t	available	verified	active	2026-02-25 04:43:05.891971	2026-06-05 04:43:05.891971
33	9	Student Hostel near Ratnanagar	Cozy and well-furnished property perfect for students and young professionals. Nearby restaurants, cafes, and entertainment options. Flexible lease terms available.	hostel	7500.00	Bagmati	Chitwan	Chitwan	Ratnanagar	Ratnanagar, Chitwan, Nepal	27.5468	84.360278	1	1	f	f	available	pending	active	2026-02-22 04:43:05.892969	2026-06-05 04:43:05.892969
34	9	Family House in Katunje	Well-maintained property with excellent ventilation and natural light. Located in a quiet neighborhood with easy access to public transport, markets, and schools. Ideal for families and working professionals.	house	20000.00	Bagmati	Bhaktapur	Bhaktapur	Katunje	Katunje, Bhaktapur, Nepal	27.680636	85.447688	4	3	t	f	available	verified	active	2026-01-14 04:43:05.894964	2026-06-05 04:43:05.894964
35	9	Modern 2BHK Flat in Pulchowk	Well-maintained property with excellent ventilation and natural light. Located in a quiet neighborhood with easy access to public transport, markets, and schools. Ideal for families and working professionals.	flat	23500.00	Bagmati	Lalitpur	Lalitpur	Pulchowk	Pulchowk, Lalitpur, Nepal	27.664894	85.305982	2	1	t	f	available	verified	active	2025-12-31 04:43:05.895962	2026-06-05 04:43:05.896968
36	9	Budget Room in Suryabinayak	Clean and comfortable property at an affordable price. The neighborhood is safe and friendly. All essential amenities within walking distance.	room	4000.00	Bagmati	Bhaktapur	Bhaktapur	Suryabinayak	Suryabinayak, Bhaktapur, Nepal	27.686058	85.414864	1	1	f	f	available	pending	active	2026-02-01 04:43:05.897975	2026-06-05 04:43:05.897975
\.


--
-- Data for Name: property_amenities; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.property_amenities (id, property_id, amenity_id) FROM stdin;
1	1	11
2	1	4
3	2	15
4	2	19
5	2	12
6	3	14
7	3	4
8	3	16
9	3	5
10	4	20
11	4	7
12	5	14
13	5	19
14	6	1
15	6	16
16	6	3
17	6	8
18	7	17
19	7	8
20	7	18
21	7	9
22	8	9
23	8	3
24	8	5
25	8	11
26	8	4
27	9	20
28	9	12
29	9	15
30	10	10
31	10	16
32	10	18
33	10	13
34	11	12
35	11	9
36	12	13
37	12	6
38	13	7
39	13	8
40	13	12
41	14	4
42	14	13
43	14	18
44	14	9
45	15	9
46	15	20
47	15	15
48	16	16
49	16	15
50	16	1
51	16	9
52	17	10
53	17	2
54	17	12
55	17	7
56	17	13
57	18	15
58	18	1
59	18	8
60	19	16
61	19	8
62	19	19
63	19	11
64	20	13
65	20	4
66	20	6
67	20	1
68	21	1
69	21	2
70	21	12
71	22	4
72	22	12
73	23	18
74	23	17
75	23	10
76	23	19
77	23	8
78	24	20
79	24	4
80	24	8
81	24	10
82	24	18
83	25	18
84	25	16
85	25	1
86	26	13
87	26	14
88	26	5
89	27	9
90	27	15
91	27	3
92	27	7
93	27	13
94	28	13
95	28	17
96	28	16
97	28	14
98	28	12
99	29	19
100	29	1
101	29	13
102	29	10
103	29	3
104	30	18
105	30	8
106	30	11
107	30	10
108	30	12
109	31	8
110	31	1
111	31	18
112	32	7
113	32	15
114	32	10
115	32	18
116	33	20
117	33	3
118	34	2
119	34	18
120	35	1
121	35	12
122	35	13
123	36	11
124	36	16
125	36	12
126	36	13
127	36	14
\.


--
-- Data for Name: property_documents; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.property_documents (id, property_id, document_type, document_file, verification_status, created_at) FROM stdin;
\.


--
-- Data for Name: property_images; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.property_images (id, property_id, image_path, created_at) FROM stdin;
1	1	https://images.unsplash.com/photo-1568605114967-8130f3a36994?w=600&q=80	2026-06-05 04:43:05.333173
2	2	https://images.unsplash.com/photo-1571939228382-b2f2b585ce15?w=600&q=80	2026-06-05 04:43:05.341171
3	3	https://images.unsplash.com/photo-1571939228382-b2f2b585ce15?w=600&q=80	2026-06-05 04:43:05.345168
4	4	https://images.unsplash.com/photo-1568605114967-8130f3a36994?w=600&q=80	2026-06-05 04:43:05.350167
5	5	https://images.unsplash.com/photo-1599619351208-3e6c839d6828?w=600&q=80	2026-06-05 04:43:05.419968
6	6	https://images.unsplash.com/photo-1568605114967-8130f3a36994?w=600&q=80	2026-06-05 04:43:05.420907
7	7	https://images.unsplash.com/photo-1484154218962-a197022b5858?w=600&q=80	2026-06-05 04:43:05.424907
8	8	https://images.unsplash.com/photo-1571939228382-b2f2b585ce15?w=600&q=80	2026-06-05 04:43:05.495671
9	9	https://images.unsplash.com/photo-1484154218962-a197022b5858?w=600&q=80	2026-06-05 04:43:05.499679
10	10	https://images.unsplash.com/photo-1493809842364-78817add7ffb?w=600&q=80	2026-06-05 04:43:05.499679
11	11	https://images.unsplash.com/photo-1502672260266-1c1ef2d93688?w=600&q=80	2026-06-05 04:43:05.50462
12	12	https://images.unsplash.com/photo-1555041469-a586c61ea9bc?w=600&q=80	2026-06-05 04:43:05.505665
13	13	https://images.unsplash.com/photo-1583608205776-bfd35f0d9f83?w=600&q=80	2026-06-05 04:43:05.583399
14	14	https://images.unsplash.com/photo-1522708323590-d24dbb6b0267?w=600&q=80	2026-06-05 04:43:05.586398
15	15	https://images.unsplash.com/photo-1599619351208-3e6c839d6828?w=600&q=80	2026-06-05 04:43:05.5874
16	16	https://images.unsplash.com/photo-1536376072261-38c75010e6c9?w=600&q=80	2026-06-05 04:43:05.589402
17	17	https://images.unsplash.com/photo-1484154218962-a197022b5858?w=600&q=80	2026-06-05 04:43:05.590919
18	18	https://images.unsplash.com/photo-1522708323590-d24dbb6b0267?w=600&q=80	2026-06-05 04:43:05.661965
19	19	https://images.unsplash.com/photo-1484154218962-a197022b5858?w=600&q=80	2026-06-05 04:43:05.666034
20	20	https://images.unsplash.com/photo-1524758631624-e2822e304c36?w=600&q=80	2026-06-05 04:43:05.668029
21	21	https://images.unsplash.com/photo-1574362848149-11496d93a7c7?w=600&q=80	2026-06-05 04:43:05.735029
22	22	https://images.unsplash.com/photo-1493809842364-78817add7ffb?w=600&q=80	2026-06-05 04:43:05.738084
23	23	https://images.unsplash.com/photo-1522708323590-d24dbb6b0267?w=600&q=80	2026-06-05 04:43:05.739082
24	24	https://images.unsplash.com/photo-1555041469-a586c61ea9bc?w=600&q=80	2026-06-05 04:43:05.741027
25	25	https://images.unsplash.com/photo-1555041469-a586c61ea9bc?w=600&q=80	2026-06-05 04:43:05.743022
26	26	https://images.unsplash.com/photo-1555041469-a586c61ea9bc?w=600&q=80	2026-06-05 04:43:05.80897
27	27	https://images.unsplash.com/photo-1536376072261-38c75010e6c9?w=600&q=80	2026-06-05 04:43:05.81297
28	28	https://images.unsplash.com/photo-1555041469-a586c61ea9bc?w=600&q=80	2026-06-05 04:43:05.81397
29	29	https://images.unsplash.com/photo-1502672260266-1c1ef2d93688?w=600&q=80	2026-06-05 04:43:05.815968
30	30	https://images.unsplash.com/photo-1583608205776-bfd35f0d9f83?w=600&q=80	2026-06-05 04:43:05.81796
31	31	https://images.unsplash.com/photo-1599619351208-3e6c839d6828?w=600&q=80	2026-06-05 04:43:05.890971
32	32	https://images.unsplash.com/photo-1556020685-ae41abfc9365?w=600&q=80	2026-06-05 04:43:05.893966
33	33	https://images.unsplash.com/photo-1484154218962-a197022b5858?w=600&q=80	2026-06-05 04:43:05.895962
34	34	https://images.unsplash.com/photo-1493809842364-78817add7ffb?w=600&q=80	2026-06-05 04:43:05.897975
35	35	https://images.unsplash.com/photo-1555041469-a586c61ea9bc?w=600&q=80	2026-06-05 04:43:05.89897
36	36	https://images.unsplash.com/photo-1560185127-6ed189bf02f4?w=600&q=80	2026-06-05 04:43:05.899969
\.


--
-- Data for Name: reports; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.reports (id, reported_by, property_id, reason, status, created_at) FROM stdin;
\.


--
-- Data for Name: reviews; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.reviews (id, property_id, user_id, rating, review, created_at) FROM stdin;
1	27	10	4	Decent place but could use some minor repairs. Overall a good experience.	2026-03-07 04:43:06.578558
2	8	11	5	Decent place but could use some minor repairs. Overall a good experience.	2026-04-19 04:43:06.578558
3	9	12	4	Excellent property with all amenities. The owner responds quickly to any issues.	2026-04-16 04:43:06.578558
4	25	12	5	Excellent property with all amenities. The owner responds quickly to any issues.	2026-04-20 04:43:06.578558
5	4	12	3	Great place to live! The owner is very cooperative and the neighborhood is peaceful.	2026-05-19 04:43:06.578558
6	21	13	4	Very clean and well-maintained property. Highly recommended for families.	2026-04-25 04:43:06.578558
7	16	14	4	Very clean and well-maintained property. Highly recommended for families.	2026-04-16 04:43:06.578558
8	3	14	5	Good location with easy access to public transport. Value for money.	2026-05-15 04:43:06.578558
9	7	14	4	Decent place but could use some minor repairs. Overall a good experience.	2026-04-02 04:43:06.578558
10	5	15	5	Decent place but could use some minor repairs. Overall a good experience.	2026-05-13 04:43:06.578558
11	6	16	3	The kitchen and bathroom are well-maintained. Would definitely recommend.	2026-04-20 04:43:06.578558
12	5	16	3	The property is exactly as described. Happy with my decision to rent here.	2026-05-28 04:43:06.578558
13	3	17	4	The property is exactly as described. Happy with my decision to rent here.	2026-04-11 04:43:06.579584
14	7	18	5	Nice and quiet neighborhood. The property has great ventilation and natural light.	2026-03-16 04:43:06.579584
15	32	18	4	Good location with easy access to public transport. Value for money.	2026-03-07 04:43:06.579584
16	24	18	3	Nice and quiet neighborhood. The property has great ventilation and natural light.	2026-04-09 04:43:06.579584
17	18	19	4	Nice and quiet neighborhood. The property has great ventilation and natural light.	2026-03-09 04:43:06.579584
18	14	19	4	The property is exactly as described. Happy with my decision to rent here.	2026-06-04 04:43:06.579584
19	20	19	5	Nice and quiet neighborhood. The property has great ventilation and natural light.	2026-03-19 04:43:06.579584
\.


--
-- Data for Name: roommate_profiles; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.roommate_profiles (id, user_id, preferred_city, budget, occupation, gender_preference, smoking_preference, drinking_preference, lifestyle, bio, created_at) FROM stdin;
1	10	Kathmandu	15000.00	Business Person	Any	Yes	Occasionally	Flexible	Hi, I am Anita, a Business Person looking for a comfortable place to stay.	2026-06-05 04:43:06.029969
2	12	Butwal	5000.00	Doctor	Male	No	No	Flexible	Hi, I am Priya, a Doctor looking for a comfortable place to stay.	2026-06-05 04:43:06.166185
3	13	Bhaktapur	12000.00	Programmer	Female	No	No	Flexible	Hi, I am Suresh, a Programmer looking for a comfortable place to stay.	2026-06-05 04:43:06.232198
4	14	Lalitpur	8000.00	Teacher	Female	No	Occasionally	Flexible	Hi, I am Binita, a Teacher looking for a comfortable place to stay.	2026-06-05 04:43:06.298188
5	17	Dharan	15000.00	Teacher	Any	No	Occasionally	Flexible	Hi, I am Arun, a Teacher looking for a comfortable place to stay.	2026-06-05 04:43:06.495199
6	19	Dhangadhi	5000.00	Student	Any	No	No	Early riser	Hi, I am Dipesh, a Student looking for a comfortable place to stay.	2026-06-05 04:43:06.561183
\.


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.users (id, full_name, email, phone, password, role, gender, occupation, profile_image, province, district, city, address, account_status, created_at, updated_at, profile_complete) FROM stdin;
1	Admin RentSathi	admin@rentsathi.com.np	+977-1-4567890	scrypt:32768:8:1$1Yvq2wNJPg9clcNK$9490638ee26b89d450d42559df1dfed1b1f82736cd77a0c896524469e2c21b11a5f30e41c9c3353dfd39d26b166e25428d761c59306b4821160bacd1ce9d9f8f	admin	\N	\N	\N	Bagmati	Kathmandu	Kathmandu	\N	active	2026-06-05 04:43:05.223584	2026-06-05 04:43:05.223584	f
2	Ramesh Sharma	ramesh@example.com	+977-9841234567	scrypt:32768:8:1$fnjPj9kLlMbKxc1A$2dbcdf03010987175a28f6fceba54a9f839e6faf2a059eda27b56f87218cea917d77663faf3a89fd5861b9ad3f082e46a8111a02ac1bbd608c06a2e311677a02	owner	Male	Property Owner	\N	\N	\N	Chitwan	\N	active	2025-12-08 04:43:05.325172	2026-06-05 04:43:05.326177	f
3	Sunita Thapa	sunita@example.com	+977-9842345678	scrypt:32768:8:1$YoTzlPyveox5zfHr$790de779793765fdd534b803093ea8454b76fbdc2cd6916ce99e5439dc8249e199378b405ecf4611f0bdbc82a816fbe2cd00e561eeb5f83b01c89583d2e6f5ea	owner	Male	Property Owner	\N	\N	\N	Biratnagar	\N	active	2026-04-13 04:43:05.415962	2026-06-05 04:43:05.416966	f
4	Bikash Pradhan	bikash@example.com	+977-9843456789	scrypt:32768:8:1$0ScKwNCTubWyYIct$2a22bea9d619aa19ef1c12b2924575e61a78f9678729a6d329f4b965ba0ab54710ea497b306c96619c118a64d38ae5a2fea2144fa6fec158e86a5d2e445180a6	owner	Male	Property Owner	\N	\N	\N	Biratnagar	\N	active	2025-09-24 04:43:05.494668	2026-06-05 04:43:05.495671	f
5	Sita Gurung	sita@example.com	+977-9844567890	scrypt:32768:8:1$sIyb8ertrmNgxSpl$1ef2bdb3c9ff2cb7c29da45ad075d004a5b53f8e4fc5d2959f1738b4f1d35a7e7715bf7cbc6d9bab20a37f4ae3ccdc3b4952fa0ce1179682ad077bf5a1bf9778	owner	Female	Property Owner	\N	\N	\N	Dhangadhi	\N	active	2025-07-16 04:43:05.5824	2026-06-05 04:43:05.583399	f
6	Deepak Karki	deepak@example.com	+977-9845678901	scrypt:32768:8:1$npHeYN6vNlojW2lJ$7cb35a7d62cab7619e65182ae6de4e9f662b2881222f486d55d4ee52b7220bf4cb47f47e75a788b87223ccdec51fb713fc44295f0db3e0665ed1090fc8c3a928	owner	Male	Property Owner	\N	\N	\N	Chitwan	\N	active	2025-07-05 04:43:05.660961	2026-06-05 04:43:05.662959	f
7	Hari Adhikari	hari@example.com	+977-9846789012	scrypt:32768:8:1$32MVb8HIemuqt9W8$b8a6307545aea21598ae99af92eb265130177fc1ce538d87ce98c859a74343a55d0317fbf1bec7c2e0c0a009f11fedfe61b7e7729e90b82b8bef20176c2d964d	owner	Male	Property Owner	\N	\N	\N	Kathmandu	\N	active	2025-07-06 04:43:05.734027	2026-06-05 04:43:05.735029	f
8	Mina Shrestha	mina@example.com	+977-9847890123	scrypt:32768:8:1$cKjK3CuOC2ZPbXyu$e5ee05416255ee444e725f8175a67c6ef99f75f656444cdc437d9af40684e060c6c7de19c683c07b314d74d4f483d2ac82aca0ae6806f4b47bbd7e42dbab104d	owner	Male	Property Owner	\N	\N	\N	Birgunj	\N	active	2025-11-10 04:43:05.807969	2026-06-05 04:43:05.80997	f
9	Prakash Tamang	prakash@example.com	+977-9848901234	scrypt:32768:8:1$SS0GZM5Srs5gPKak$dd8e3fb72618364315d8d8c174fe0e8a871532f6799ff8a14327358100b7ab1a4d3a0146fea95dd2963dcf64b19206c55d8b286d6ca10cf432f4465073a9ff2e	owner	Female	Property Owner	\N	\N	\N	Bhaktapur	\N	active	2025-06-16 04:43:05.889961	2026-06-05 04:43:05.890971	f
10	Anita Maharjan	anita@example.com	+977-9851234567	scrypt:32768:8:1$JJCVwgXSaAZHAzKx$0bf763152725b2a754fbc58668e3bde1792dd2f0f0f0bf2441c58dd18c9469643751e9966a76c6d6188a47bb2663bd6574318a0dc563119252873cd7a05ae8c5	user	Male	Business Person	\N	Bagmati	Kathmandu	Kathmandu	\N	active	2026-03-05 04:43:05.963958	2026-06-05 04:43:05.964958	f
11	Rajesh Tamang	rajesh@example.com	+977-9852345678	scrypt:32768:8:1$s8D1odQ3ccajgfpL$c9cfeef0f1d9779fbd1ac541b2e18eb784c7da12c60186848f81a4ad8397f97e67552b006b2da03709e579d55c56ab133c3dfb3d63a3c8bed383670cd9431ffc	user	Male	Business Person	\N	Gandaki	Kaski	Pokhara	\N	active	2026-05-10 04:43:06.028969	2026-06-05 04:43:06.028969	f
12	Priya Adhikari	priya@example.com	+977-9853456789	scrypt:32768:8:1$VuIvK2JCVSvLFteV$f1bb4d4f10d5056104221dc4a052337aa2739ccd1f5ddc874a3ff1049daad7ef4df0165d7f4c189201d3e03342dd05d85de5894db5fe008b004d6cfcdcb97436	user	Female	Doctor	\N	Lumbini	Rupandehi	Butwal	\N	active	2026-04-25 04:43:06.097968	2026-06-05 04:43:06.097968	f
13	Suresh KC	suresh@example.com	+977-9854567890	scrypt:32768:8:1$IX18VrsqjTHc24bm$499970eb23aac4ba0ed897c13129ec36a9b0862c15c4f1132469da13d87a16bc5719d46416a03947e3136c82b9c8097b9e29c0a1e2ac7c7c8e71ac7c2995e0d1	user	Male	Programmer	\N	Bagmati	Bhaktapur	Bhaktapur	\N	active	2026-05-26 04:43:06.165188	2026-06-05 04:43:06.165188	f
14	Binita Rai	binita@example.com	+977-9855678901	scrypt:32768:8:1$ZVLHXV9151CftsxF$9fbaa4aa922ea433bc5481cef383fb58547fec8c4c902a154287f90bacd4adc22a4c4f25f285527f6172e55f932a47386e7e4fef0e1a28bfc2108387a5319907	user	Male	Teacher	\N	Bagmati	Lalitpur	Lalitpur	\N	active	2026-02-10 04:43:06.231202	2026-06-05 04:43:06.231202	f
15	Nabin Limbu	nabin@example.com	+977-9856789012	scrypt:32768:8:1$ZMLSYg65DSQ5L3rS$9a9b78d493fe8e9aff61d0a18f3634c064cce628e1304b37bb72901f30e435d266b8276a3e78f3963a1e4cb861bd3f54a1eac04f6c3d1813c8d033b6572da9da	user	Female	Business Person	\N	Gandaki	Kaski	Pokhara	\N	active	2025-12-08 04:43:06.296187	2026-06-05 04:43:06.297187	f
16	Kavita Basnet	kavita@example.com	+977-9857890123	scrypt:32768:8:1$v29lcYDjvcCVzx9U$90936aa6e59e224572b68f3228ca28f7a6fd815f1782466e655754eb8da60f0c8102b196fdade707727e73ac308e01f835d42e72be8a16bec6c17f8c3f42c0df	user	Female	Business Person	\N	Bagmati	Kathmandu	Kathmandu	\N	active	2026-05-14 04:43:06.364187	2026-06-05 04:43:06.364187	f
17	Arun Pokharel	arun@example.com	+977-9858901234	scrypt:32768:8:1$NQXslk46EPFytKuf$e2f81a2754036c82cc67d3ff8d700ea45fdfe4c89027bf7a66b60e0f6d5806c266c0ca96e21772cbc2f61dca8adf7537bb34a91413a37f514c4821fdcb80093f	user	Male	Teacher	\N	Koshi	Sunsari	Dharan	\N	active	2025-11-28 04:43:06.428187	2026-06-05 04:43:06.428187	f
18	Sangita Bista	sangita@example.com	+977-9859012345	scrypt:32768:8:1$dJ2l7i2UOk9vg41u$19636eb1ea49fc599805a49500d9bfdcaa454fa1bc0825b3e251cbfd4b3eebf9625205146107103ce06e5257057b727b09e5d6df0198ef8395e56b2c10ee677b	user	Female	Business Person	\N	Gandaki	Kaski	Pokhara	\N	active	2026-02-12 04:43:06.494198	2026-06-05 04:43:06.494198	f
19	Dipesh Magar	dipesh@example.com	+977-9850123456	scrypt:32768:8:1$1NJWme476d8ataJz$bf1dfb416c21377dbe5a7db01a56e59927c65548680c1f35a75c8e18b454710d98ecb8bb2c18917622584909ac6e0686d36b5394ad70218be3ff719a0bdfd6b4	user	Female	Student	\N	Sudurpashchim	Kailali	Dhangadhi	\N	active	2026-03-30 04:43:06.560187	2026-06-05 04:43:06.560187	f
\.


--
-- Data for Name: vacancy_calendar; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.vacancy_calendar (id, property_id, available_from, available_until, status) FROM stdin;
\.


--
-- Name: admin_logs_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.admin_logs_id_seq', 1, false);


--
-- Name: amenities_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.amenities_id_seq', 20, true);


--
-- Name: chats_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.chats_id_seq', 20, true);


--
-- Name: favorites_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.favorites_id_seq', 27, true);


--
-- Name: owner_profiles_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.owner_profiles_id_seq', 8, true);


--
-- Name: properties_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.properties_id_seq', 36, true);


--
-- Name: property_amenities_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.property_amenities_id_seq', 127, true);


--
-- Name: property_documents_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.property_documents_id_seq', 1, false);


--
-- Name: property_images_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.property_images_id_seq', 36, true);


--
-- Name: reports_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.reports_id_seq', 1, false);


--
-- Name: reviews_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.reviews_id_seq', 19, true);


--
-- Name: roommate_profiles_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.roommate_profiles_id_seq', 6, true);


--
-- Name: users_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.users_id_seq', 19, true);


--
-- Name: vacancy_calendar_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.vacancy_calendar_id_seq', 1, false);


--
-- Name: admin_logs admin_logs_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.admin_logs
    ADD CONSTRAINT admin_logs_pkey PRIMARY KEY (id);


--
-- Name: alembic_version alembic_version_pkc; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.alembic_version
    ADD CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num);


--
-- Name: amenities amenities_amenity_name_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.amenities
    ADD CONSTRAINT amenities_amenity_name_key UNIQUE (amenity_name);


--
-- Name: amenities amenities_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.amenities
    ADD CONSTRAINT amenities_pkey PRIMARY KEY (id);


--
-- Name: chats chats_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.chats
    ADD CONSTRAINT chats_pkey PRIMARY KEY (id);


--
-- Name: favorites favorites_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.favorites
    ADD CONSTRAINT favorites_pkey PRIMARY KEY (id);


--
-- Name: owner_profiles owner_profiles_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.owner_profiles
    ADD CONSTRAINT owner_profiles_pkey PRIMARY KEY (id);


--
-- Name: owner_profiles owner_profiles_user_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.owner_profiles
    ADD CONSTRAINT owner_profiles_user_id_key UNIQUE (user_id);


--
-- Name: properties properties_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.properties
    ADD CONSTRAINT properties_pkey PRIMARY KEY (id);


--
-- Name: property_amenities property_amenities_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.property_amenities
    ADD CONSTRAINT property_amenities_pkey PRIMARY KEY (id);


--
-- Name: property_documents property_documents_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.property_documents
    ADD CONSTRAINT property_documents_pkey PRIMARY KEY (id);


--
-- Name: property_images property_images_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.property_images
    ADD CONSTRAINT property_images_pkey PRIMARY KEY (id);


--
-- Name: reports reports_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.reports
    ADD CONSTRAINT reports_pkey PRIMARY KEY (id);


--
-- Name: reviews reviews_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.reviews
    ADD CONSTRAINT reviews_pkey PRIMARY KEY (id);


--
-- Name: roommate_profiles roommate_profiles_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.roommate_profiles
    ADD CONSTRAINT roommate_profiles_pkey PRIMARY KEY (id);


--
-- Name: roommate_profiles roommate_profiles_user_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.roommate_profiles
    ADD CONSTRAINT roommate_profiles_user_id_key UNIQUE (user_id);


--
-- Name: favorites uq_user_property_favorite; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.favorites
    ADD CONSTRAINT uq_user_property_favorite UNIQUE (user_id, property_id);


--
-- Name: users users_email_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_email_key UNIQUE (email);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: vacancy_calendar vacancy_calendar_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.vacancy_calendar
    ADD CONSTRAINT vacancy_calendar_pkey PRIMARY KEY (id);


--
-- Name: admin_logs admin_logs_admin_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.admin_logs
    ADD CONSTRAINT admin_logs_admin_id_fkey FOREIGN KEY (admin_id) REFERENCES public.users(id);


--
-- Name: chats chats_property_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.chats
    ADD CONSTRAINT chats_property_id_fkey FOREIGN KEY (property_id) REFERENCES public.properties(id);


--
-- Name: chats chats_receiver_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.chats
    ADD CONSTRAINT chats_receiver_id_fkey FOREIGN KEY (receiver_id) REFERENCES public.users(id);


--
-- Name: chats chats_sender_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.chats
    ADD CONSTRAINT chats_sender_id_fkey FOREIGN KEY (sender_id) REFERENCES public.users(id);


--
-- Name: favorites favorites_property_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.favorites
    ADD CONSTRAINT favorites_property_id_fkey FOREIGN KEY (property_id) REFERENCES public.properties(id);


--
-- Name: favorites favorites_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.favorites
    ADD CONSTRAINT favorites_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: owner_profiles owner_profiles_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.owner_profiles
    ADD CONSTRAINT owner_profiles_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: properties properties_owner_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.properties
    ADD CONSTRAINT properties_owner_id_fkey FOREIGN KEY (owner_id) REFERENCES public.users(id);


--
-- Name: property_amenities property_amenities_amenity_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.property_amenities
    ADD CONSTRAINT property_amenities_amenity_id_fkey FOREIGN KEY (amenity_id) REFERENCES public.amenities(id);


--
-- Name: property_amenities property_amenities_property_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.property_amenities
    ADD CONSTRAINT property_amenities_property_id_fkey FOREIGN KEY (property_id) REFERENCES public.properties(id);


--
-- Name: property_documents property_documents_property_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.property_documents
    ADD CONSTRAINT property_documents_property_id_fkey FOREIGN KEY (property_id) REFERENCES public.properties(id);


--
-- Name: property_images property_images_property_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.property_images
    ADD CONSTRAINT property_images_property_id_fkey FOREIGN KEY (property_id) REFERENCES public.properties(id);


--
-- Name: reports reports_property_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.reports
    ADD CONSTRAINT reports_property_id_fkey FOREIGN KEY (property_id) REFERENCES public.properties(id);


--
-- Name: reports reports_reported_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.reports
    ADD CONSTRAINT reports_reported_by_fkey FOREIGN KEY (reported_by) REFERENCES public.users(id);


--
-- Name: reviews reviews_property_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.reviews
    ADD CONSTRAINT reviews_property_id_fkey FOREIGN KEY (property_id) REFERENCES public.properties(id);


--
-- Name: reviews reviews_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.reviews
    ADD CONSTRAINT reviews_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: roommate_profiles roommate_profiles_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.roommate_profiles
    ADD CONSTRAINT roommate_profiles_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: vacancy_calendar vacancy_calendar_property_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.vacancy_calendar
    ADD CONSTRAINT vacancy_calendar_property_id_fkey FOREIGN KEY (property_id) REFERENCES public.properties(id);


--
-- PostgreSQL database dump complete
--

\unrestrict sdvWXDvMPbAyf1oUA0lP09YuW2p8GGh3uFQa9PPkCcy6p9OlN26ADts3nlBCTH2

