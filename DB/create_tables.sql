/*
    -- EUROPEAN PARLIAMENT PROJECT DB --

Author: Morgan Séguéla

Version:
    V0.1: First creation and local implementation
    V0.2: Moving sits_on table and add information about text and vote content
*/

/*
    DROP ALL TABLES
*/
DROP TABLE IF EXISTS project.votes;
DROP TABLE IF EXISTS project.sits_on;
DROP TABLE IF EXISTS project.voteContent;

DROP TABLE IF EXISTS project.text;
DROP TABLE IF EXISTS project.minute;

DROP TABLE IF EXISTS project.voteValue;

DROP TABLE IF EXISTS project.parliamentarian;
DROP TABLE IF EXISTS project.political_group;
DROP TABLE IF EXISTS project.national_political_group;
DROP TABLE IF EXISTS project.country;

DROP TABLE IF EXISTS project.seat;
DROP TABLE IF EXISTS project.parliament;


/* ====== PARLIAMENTARIAN INFORMATION ======= */
/* ========================================== */
-- Table: project.PoliticGroup
CREATE TABLE IF NOT EXISTS project.political_group
(
    pg_id integer NOT NULL,
    pg_name character varying(128) COLLATE pg_catalog."default" NOT NULL,
    pg_abrv character varying(8) COLLATE pg_catalog."default" NOT NULL,
    CONSTRAINT pk_politicalgroup PRIMARY KEY (pg_id)
);

ALTER TABLE IF EXISTS project.political_group
    OWNER to postgres;

GRANT SELECT ON TABLE project.political_group TO PUBLIC;

GRANT ALL ON TABLE project.political_group TO postgres;

COMMENT ON TABLE project.political_group
    IS 'Politic group inside the parliament in which the parliamentarian is.';

-- Table: project.NationalPoliticalGroup
CREATE TABLE IF NOT EXISTS project.national_political_group
(
    npg_id integer NOT NULL,
    npg_name character varying(128) COLLATE pg_catalog."default" NOT NULL,
    CONSTRAINT pk_npg PRIMARY KEY (npg_id)
);

ALTER TABLE IF EXISTS project.national_political_group
    OWNER to postgres;

GRANT SELECT ON TABLE project.national_political_group TO PUBLIC;

GRANT ALL ON TABLE project.national_political_group TO postgres;

COMMENT ON TABLE project.national_political_group
    IS 'Represent the national political group of the parliamentarian';


-- Table: project.country

CREATE TABLE IF NOT EXISTS project.country
(
    country_id integer NOT NULL,
    country_name character varying(128) COLLATE pg_catalog."default" NOT NULL,
    CONSTRAINT pk_country PRIMARY KEY (country_id)
);

ALTER TABLE IF EXISTS project.country
    OWNER to postgres;

GRANT SELECT ON TABLE project.country TO PUBLIC;

GRANT ALL ON TABLE project.country TO postgres;

COMMENT ON TABLE project.country
    IS 'Represent the parliamentarian country';


-- Table: project.Parliamentarian
CREATE TABLE IF NOT EXISTS project.parliamentarian
(
    parliamentarian_id integer NOT NULL,
    p_fullname character varying(64) COLLATE pg_catalog."default",
    country_id integer,
    npg_id integer,
    pg_id integer,
    CONSTRAINT pk_parliamentarian PRIMARY KEY (parliamentarian_id),
    CONSTRAINT fk_parliamentarian_npg FOREIGN KEY (npg_id)
        REFERENCES project.national_political_group (npg_id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION,
    CONSTRAINT fk_parliamentarian_country FOREIGN KEY (country_id)
        REFERENCES project.country (country_id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION,
    CONSTRAINT fk_parliamentarian_pg FOREIGN KEY (pg_id)
        REFERENCES project.political_group(pg_id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
);

ALTER TABLE IF EXISTS project.parliamentarian
    OWNER to postgres;

GRANT SELECT ON TABLE project.parliamentarian TO PUBLIC;

GRANT ALL ON TABLE project.parliamentarian TO postgres;

COMMENT ON TABLE project.parliamentarian
    IS 'Member of parliamentary';



/* ======= Vote information ======== */
/* ================================= */
-- Table: project.VoteValue
CREATE TABLE IF NOT EXISTS project.voteValue
(
    vote_id integer NOT NULL,
    vote_name character varying(16) COLLATE pg_catalog."default" NOT NULL,
    vote_value integer NOT NULL,
    CONSTRAINT pk_votevalue PRIMARY KEY (vote_id)
);

ALTER TABLE IF EXISTS project.voteValue
    OWNER to postgres;

GRANT SELECT ON TABLE project.voteValue TO PUBLIC;

GRANT ALL ON TABLE project.voteValue TO postgres;

COMMENT ON TABLE project.voteValue
    IS 'Value of choices during votes : abstention, for, against, missing';


-- Table: project.Text
CREATE TABLE IF NOT EXISTS project.text
(
    text_id integer NOT NULL,
    reference character varying(16) COLLATE pg_catalog."default" NOT NULL,
    description text COLLATE pg_catalog."default",
    url character varying(256) COLLATE pg_catalog."default" NOT NULL,
    CONSTRAINT pk_text PRIMARY KEY (text_id)
);

ALTER TABLE IF EXISTS project.text
    OWNER to postgres;

GRANT SELECT ON TABLE project.text TO PUBLIC;

GRANT ALL ON TABLE project.text TO postgres;

COMMENT ON TABLE project.text
    IS 'Text submitted to parliamentarian votes.';


-- Table: project.Minutes
CREATE TABLE IF NOT EXISTS project.minute
(
    minute_id integer NOT NULL,
    minute_date date NOT NULL,
    minute_url character varying(128) COLLATE pg_catalog."default" NOT NULL,
    CONSTRAINT pk_minute PRIMARY KEY (minute_id)
);

ALTER TABLE IF EXISTS project.minute
    OWNER to postgres;

GRANT SELECT ON TABLE project.minute TO PUBLIC;

GRANT ALL ON TABLE project.minute TO postgres;


-- Table: project.voteContent
CREATE TABLE IF NOT EXISTS project.voteContent
(
    content_id integer NOT NULL,
    desscription text NOT NULL COLLATE pg_catalog."default" NOT NULL,
    text_id integer,
    minute_id integer NOT NULL,
    CONSTRAINT pk_voteContent PRIMARY KEY (content_id),
    CONSTRAINT fk_content_text FOREIGN KEY (text_id) REFERENCES project.text(text_id),
    CONSTRAINT fk_content_minute FOREIGN KEY (minute_id) REFERENCES project.minute(minute_id)
);

ALTER TABLE IF EXISTS project.voteContent
    OWNER to postgres;

GRANT SELECT ON TABLE project.voteContent TO PUBLIC;

GRANT ALL ON TABLE project.voteContent TO postgres;


-- Table: project.votes
CREATE TABLE IF NOT EXISTS project.votes
(
    parliamentarian_id integer NOT NULL,
    content_id integer NOT NULL,
    vote_time timestamp with time zone NOT NULL,
    final_vote_id integer,
    intention_vote_id integer,
    seat_id integer,
    CONSTRAINT pk_votes PRIMARY KEY (parliamentarian_id, content_id, vote_time),
    CONSTRAINT fk_votes_vote_value_choice FOREIGN KEY (final_vote_id)
        REFERENCES project.voteValue (vote_id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION,
    CONSTRAINT fk_votes_vote_value_intention FOREIGN KEY (intention_vote_id)
        REFERENCES project.voteValue (vote_id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION,
    CONSTRAINT fk_votes_parliamentarian FOREIGN KEY (parliamentarian_id)
        REFERENCES project.parliamentarian (parliamentarian_id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION,
    CONSTRAINT fk_votes_content FOREIGN KEY (content_id)
        REFERENCES project.voteContent (content_id)
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
);

ALTER TABLE IF EXISTS project.votes
    OWNER to postgres;

GRANT SELECT ON TABLE project.votes TO PUBLIC;

GRANT ALL ON TABLE project.votes TO postgres;

COMMENT ON TABLE project.votes
    IS 'votes of each parliamentarian for each content for a given time';

COMMENT ON CONSTRAINT fk_votes_content ON project.votes
    IS 'Correspond to the content voted taken into account';
COMMENT ON CONSTRAINT fk_votes_vote_value_intention ON project.votes
    IS 'Corresponds to the intention of vote. A first vote before it is rectified.';


/* ======== Seat and Parliament Information ======== */
/* ================================================= */
-- Table: project.Parliament
CREATE TABLE IF NOT EXISTS project.parliament
(
    parliament_id integer NOT NULL,
    parliament_name character varying(16) COLLATE pg_catalog."default" NOT NULL,
    parliament_abr character varying(3) COLLATE pg_catalog."default" NOT NULL,
    CONSTRAINT pk_parliament PRIMARY KEY (parliament_id)
);

ALTER TABLE IF EXISTS project.parliament
    OWNER to postgres;

GRANT SELECT ON TABLE project.parliament TO PUBLIC;

GRANT ALL ON TABLE project.parliament TO postgres;

COMMENT ON TABLE project.parliament
    IS 'Parliament, correspond to Brussels or Strasbourg';


-- Table: project.Seat
CREATE TABLE project.seat
(
    seat_id integer,
    seat_number integer,
    seat_xpos integer,
    seat_ypos integer,
    square_size_x integer,
    square_size_y integer,
    use character varying(16),
    parliament_id integer,
    CONSTRAINT pk_seat PRIMARY KEY (seat_id),
    CONSTRAINT fk_seat_parliament FOREIGN KEY (parliament_id)
        REFERENCES project.parliament (parliament_id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
        NOT VALID
);

ALTER TABLE IF EXISTS project.seat
    OWNER to postgres;

GRANT SELECT ON TABLE project.seat TO PUBLIC;

GRANT ALL ON TABLE project.seat TO postgres;
    
COMMENT ON TABLE project.seat
    IS 'seats of each parliament';

    
-- Table: project.sits_on

CREATE TABLE IF NOT EXISTS project.sits_on
(
    parliamentarian_id integer NOT NULL,
    seat_id integer NOT NULL,
    date_sit date NOT NULL,
    CONSTRAINT pk_sits_on PRIMARY KEY (parliamentarian_id, seat_id, date_sit),
    CONSTRAINT fk_sits_on_parliamentarian FOREIGN KEY (parliamentarian_id)
        REFERENCES project.parliamentarian (parliamentarian_id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION,
    CONSTRAINT fk_sits_on_seat FOREIGN KEY (seat_id)
        REFERENCES project.seat (seat_id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
);

ALTER TABLE IF EXISTS project.sits_on
    OWNER to postgres;

GRANT SELECT ON TABLE project.sits_on TO PUBLIC;

GRANT ALL ON TABLE project.sits_on TO postgres;

COMMENT ON TABLE project.sits_on
    IS 'Seat parliamentarian sits on';    
