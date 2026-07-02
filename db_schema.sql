--
-- PostgreSQL database dump
--

\restrict tMSnTadpfEvfmMXXDDNS19jeS1RzZpvHPiJAsRw0kIJQGt2VzV1JfZ8TReforaX

-- Dumped from database version 18.1
-- Dumped by pg_dump version 18.1

-- Started on 2026-07-02 17:46:00

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
-- TOC entry 230 (class 1259 OID 25247)
-- Name: coords; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.coords (
    id bigint NOT NULL,
    latitude double precision NOT NULL,
    longitude double precision NOT NULL,
    height integer NOT NULL
);


ALTER TABLE public.coords OWNER TO postgres;

--
-- TOC entry 229 (class 1259 OID 25246)
-- Name: coords_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.coords_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.coords_id_seq OWNER TO postgres;

--
-- TOC entry 5074 (class 0 OID 0)
-- Dependencies: 229
-- Name: coords_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.coords_id_seq OWNED BY public.coords.id;


--
-- TOC entry 233 (class 1259 OID 25337)
-- Name: levels; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.levels (
    id bigint NOT NULL,
    winter character varying(2),
    summer character varying(2),
    autumn character varying(2),
    spring character varying(2)
);


ALTER TABLE public.levels OWNER TO postgres;

--
-- TOC entry 232 (class 1259 OID 25336)
-- Name: levels_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.levels_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.levels_id_seq OWNER TO postgres;

--
-- TOC entry 5075 (class 0 OID 0)
-- Dependencies: 232
-- Name: levels_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.levels_id_seq OWNED BY public.levels.id;


--
-- TOC entry 223 (class 1259 OID 25203)
-- Name: pereval_added_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.pereval_added_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.pereval_added_id_seq OWNER TO postgres;

--
-- TOC entry 220 (class 1259 OID 25183)
-- Name: pereval_added; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.pereval_added (
    id bigint DEFAULT nextval('public.pereval_added_id_seq'::regclass) NOT NULL,
    beauty_title character varying(255) NOT NULL,
    title character varying(255) NOT NULL,
    other_titles character varying(255),
    connect text,
    user_id bigint NOT NULL,
    coords_id bigint NOT NULL,
    status character varying(8) DEFAULT 'new'::character varying NOT NULL,
    date_added timestamp without time zone DEFAULT now() NOT NULL,
    add_time timestamp without time zone NOT NULL,
    levels_id bigint
);


ALTER TABLE public.pereval_added OWNER TO postgres;

--
-- TOC entry 221 (class 1259 OID 25192)
-- Name: pereval_areas_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.pereval_areas_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.pereval_areas_id_seq OWNER TO postgres;

--
-- TOC entry 222 (class 1259 OID 25193)
-- Name: pereval_areas; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.pereval_areas (
    id bigint DEFAULT nextval('public.pereval_areas_id_seq'::regclass) NOT NULL,
    id_parent bigint NOT NULL,
    title text
);


ALTER TABLE public.pereval_areas OWNER TO postgres;

--
-- TOC entry 219 (class 1259 OID 25182)
-- Name: pereval_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.pereval_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.pereval_id_seq OWNER TO postgres;

--
-- TOC entry 224 (class 1259 OID 25204)
-- Name: pereval_images; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.pereval_images (
    id bigint NOT NULL,
    date_added timestamp without time zone DEFAULT now(),
    data bytea CONSTRAINT pereval_images_img_not_null NOT NULL,
    title character varying(255) NOT NULL,
    pereval_id bigint NOT NULL
);


ALTER TABLE public.pereval_images OWNER TO postgres;

--
-- TOC entry 231 (class 1259 OID 25308)
-- Name: pereval_images_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.pereval_images_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.pereval_images_id_seq OWNER TO postgres;

--
-- TOC entry 5076 (class 0 OID 0)
-- Dependencies: 231
-- Name: pereval_images_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.pereval_images_id_seq OWNED BY public.pereval_images.id;


--
-- TOC entry 225 (class 1259 OID 25215)
-- Name: spr_activities_types_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.spr_activities_types_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.spr_activities_types_id_seq OWNER TO postgres;

--
-- TOC entry 226 (class 1259 OID 25216)
-- Name: spr_activities_types; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.spr_activities_types (
    id integer DEFAULT nextval('public.spr_activities_types_id_seq'::regclass) NOT NULL,
    title text
);


ALTER TABLE public.spr_activities_types OWNER TO postgres;

--
-- TOC entry 228 (class 1259 OID 25227)
-- Name: users; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.users (
    id bigint NOT NULL,
    email character varying(255) NOT NULL,
    name character varying(255) CONSTRAINT users_firstname_not_null NOT NULL,
    fam character varying(255) CONSTRAINT users_surname_not_null NOT NULL,
    otc character varying(255),
    phone character varying(20) NOT NULL,
    CONSTRAINT email_valid CHECK (((email)::text ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'::text)),
    CONSTRAINT phone_valid CHECK (((phone)::text ~ '^\+?[0-9\s\-\(\)]{10,20}$'::text))
);


ALTER TABLE public.users OWNER TO postgres;

--
-- TOC entry 227 (class 1259 OID 25226)
-- Name: users_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.users_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.users_id_seq OWNER TO postgres;

--
-- TOC entry 5077 (class 0 OID 0)
-- Dependencies: 227
-- Name: users_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.users_id_seq OWNED BY public.users.id;


--
-- TOC entry 4895 (class 2604 OID 25250)
-- Name: coords id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.coords ALTER COLUMN id SET DEFAULT nextval('public.coords_id_seq'::regclass);


--
-- TOC entry 4896 (class 2604 OID 25340)
-- Name: levels id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.levels ALTER COLUMN id SET DEFAULT nextval('public.levels_id_seq'::regclass);


--
-- TOC entry 4891 (class 2604 OID 25309)
-- Name: pereval_images id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.pereval_images ALTER COLUMN id SET DEFAULT nextval('public.pereval_images_id_seq'::regclass);


--
-- TOC entry 4894 (class 2604 OID 25230)
-- Name: users id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users ALTER COLUMN id SET DEFAULT nextval('public.users_id_seq'::regclass);


--
-- TOC entry 4915 (class 2606 OID 25256)
-- Name: coords coords_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.coords
    ADD CONSTRAINT coords_pkey PRIMARY KEY (id);


--
-- TOC entry 4909 (class 2606 OID 25243)
-- Name: users email_unique; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT email_unique UNIQUE (email);


--
-- TOC entry 4917 (class 2606 OID 25343)
-- Name: levels levels_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.levels
    ADD CONSTRAINT levels_pkey PRIMARY KEY (id);


--
-- TOC entry 4901 (class 2606 OID 25283)
-- Name: pereval_added pereval_added_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.pereval_added
    ADD CONSTRAINT pereval_added_pkey PRIMARY KEY (id);


--
-- TOC entry 4903 (class 2606 OID 25202)
-- Name: pereval_areas pereval_areas_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.pereval_areas
    ADD CONSTRAINT pereval_areas_pkey PRIMARY KEY (id);


--
-- TOC entry 4905 (class 2606 OID 25321)
-- Name: pereval_images pereval_images_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.pereval_images
    ADD CONSTRAINT pereval_images_pkey PRIMARY KEY (id);


--
-- TOC entry 4911 (class 2606 OID 25245)
-- Name: users phone_unique; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT phone_unique UNIQUE (phone);


--
-- TOC entry 4907 (class 2606 OID 25224)
-- Name: spr_activities_types spr_activities_types_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.spr_activities_types
    ADD CONSTRAINT spr_activities_types_pkey PRIMARY KEY (id);


--
-- TOC entry 4897 (class 2606 OID 25329)
-- Name: pereval_added status_check; Type: CHECK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE public.pereval_added
    ADD CONSTRAINT status_check CHECK (((status)::text = ANY ((ARRAY['new'::character varying, 'pending'::character varying, 'accepted'::character varying, 'rejected '::character varying])::text[]))) NOT VALID;


--
-- TOC entry 4913 (class 2606 OID 25241)
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- TOC entry 4918 (class 2606 OID 25293)
-- Name: pereval_added coords; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.pereval_added
    ADD CONSTRAINT coords FOREIGN KEY (coords_id) REFERENCES public.coords(id) NOT VALID;


--
-- TOC entry 4919 (class 2606 OID 25345)
-- Name: pereval_added levels; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.pereval_added
    ADD CONSTRAINT levels FOREIGN KEY (levels_id) REFERENCES public.levels(id) NOT VALID;


--
-- TOC entry 4921 (class 2606 OID 25322)
-- Name: pereval_images pereval; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.pereval_images
    ADD CONSTRAINT pereval FOREIGN KEY (pereval_id) REFERENCES public.pereval_added(id) NOT VALID;


--
-- TOC entry 4920 (class 2606 OID 25288)
-- Name: pereval_added user; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.pereval_added
    ADD CONSTRAINT "user" FOREIGN KEY (user_id) REFERENCES public.users(id) NOT VALID;


-- Completed on 2026-07-02 17:46:00

--
-- PostgreSQL database dump complete
--

\unrestrict tMSnTadpfEvfmMXXDDNS19jeS1RzZpvHPiJAsRw0kIJQGt2VzV1JfZ8TReforaX

