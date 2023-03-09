/*
    -- EUROPEAN PARLIAMENT PROJECT DB --

Author: Morgan Séguéla

Version:
    V0.1: First creation and local implementation
*/

DROP TABLE IF EXISTS project.votes;
DROP TABLE IF EXISTS project.sits_on;

DROP TABLE IF EXISTS project.parliamentarian;
DROP TABLE IF EXISTS project.political_group;
DROP TABLE IF EXISTS project.national_political_group;

DROP TABLE IF EXISTS project.text;
DROP TABLE IF EXISTS project.vote_value;

DROP TABLE IF EXISTS project.seat;
DROP TABLE IF EXISTS project.parliament;


-- Table: project.PoliticGroup
CREATE TABLE IF NOT EXISTS project.political_group
(
    pg_id integer NOT NULL,
    pg_name character varying(128) COLLATE pg_catalog."default" NOT NULL,
    CONSTRAINT pk_politicalgroup PRIMARY KEY (pg_id)
)

TABLESPACE pg_default;

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
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS project.national_political_group
    OWNER to postgres;

GRANT SELECT ON TABLE project.national_political_group TO PUBLIC;

GRANT ALL ON TABLE project.national_political_group TO postgres;

COMMENT ON TABLE project.national_political_group
    IS 'Represent the national political group of the parliamentarian';


-- Table: project.VoteValue
CREATE TABLE IF NOT EXISTS project.vote_value
(
    vote_id integer NOT NULL,
    vote_name character varying(16) COLLATE pg_catalog."default" NOT NULL,
    vote_value integer NOT NULL,
    CONSTRAINT pk_votevalue PRIMARY KEY (vote_id)
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS project.vote_value
    OWNER to postgres;

GRANT SELECT ON TABLE project.vote_value TO PUBLIC;

GRANT ALL ON TABLE project.vote_value TO postgres;

COMMENT ON TABLE project.vote_value
    IS 'Value of choices during votes : abstention, for, against, missing';

-- Table: project.Text
CREATE TABLE IF NOT EXISTS project.text
(
    text_id integer NOT NULL,
    reference character varying(16) COLLATE pg_catalog."default" NOT NULL,
    description text COLLATE pg_catalog."default",
    url character varying(256) COLLATE pg_catalog."default" NOT NULL,
    CONSTRAINT pk_text PRIMARY KEY (text_id)
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS project.text
    OWNER to postgres;

GRANT SELECT ON TABLE project.text TO PUBLIC;

GRANT ALL ON TABLE project.text TO postgres;

COMMENT ON TABLE project.text
    IS 'Text submitted to parliamentarian votes.';

-- Table: project.Parliament
CREATE TABLE IF NOT EXISTS project.parliament
(
    parliament_id integer NOT NULL,
    parliament_name character varying(16) COLLATE pg_catalog."default" NOT NULL,
    parliament_abr character varying(3) COLLATE pg_catalog."default" NOT NULL,
    CONSTRAINT pk_parliament PRIMARY KEY (parliament_id)
)

TABLESPACE pg_default;

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

ALTER TABLE IF EXISTS project.new_seat
    OWNER to postgres;

GRANT SELECT ON TABLE project.seat TO PUBLIC;

GRANT ALL ON TABLE project.seat TO postgres;
    
COMMENT ON TABLE project.new_seat
    IS 'seats of each parliament';

-- Table: project.Parliamentarian
CREATE TABLE IF NOT EXISTS project.parliamentarian
(
    parliamentarian_id integer NOT NULL,
    p_fullname character varying(64) COLLATE pg_catalog."default",
    country_name character varying(128) COLLATE pg_catalog."default",
    npg_id integer,
    pg_id integer,
    CONSTRAINT pk_parliamentarian PRIMARY KEY (parliamentarian_id),
    CONSTRAINT fk_parliamentarian_npg FOREIGN KEY (npg_id)
        REFERENCES project.national_political_group (npg_id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION,
    CONSTRAINT fk_parliamentarian_pg FOREIGN KEY (pg_id)
        REFERENCES project.political_group(pg_id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS project.parliamentarian
    OWNER to postgres;

GRANT SELECT ON TABLE project.parliamentarian TO PUBLIC;

GRANT ALL ON TABLE project.parliamentarian TO postgres;

COMMENT ON TABLE project.parliamentarian
    IS 'Member of parliamentary';

    
-- Table: project.sits_on

CREATE TABLE IF NOT EXISTS project.sits_on
(
    parliamentarian_id integer NOT NULL,
    seat_id integer NOT NULL,
    date date NOT NULL,
    CONSTRAINT pk_sits_on PRIMARY KEY (parliamentarian_id, seat_id, date),
    CONSTRAINT fk_sits_on_parliamentarian FOREIGN KEY (parliamentarian_id)
        REFERENCES project.parliamentarian (parliamentarian_id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION,
    CONSTRAINT fk_sits_on_seat FOREIGN KEY (seat_id)
        REFERENCES project.new_seat (seat_id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS project.sits_on
    OWNER to postgres;

GRANT SELECT ON TABLE project.sits_on TO PUBLIC;

GRANT ALL ON TABLE project.sits_on TO postgres;

COMMENT ON TABLE project.sits_on
    IS 'Seat parliamentarian sits on';    
    
    
-- Table: project.votes
CREATE TABLE IF NOT EXISTS project.votes
(
    parliamentarian_id integer NOT NULL,
    text_id integer NOT NULL,
    date date NOT NULL,
    final_vote_id integer,
    intention_vote_id integer,
    seat_id integer,
    CONSTRAINT pk_votes PRIMARY KEY (parliamentarian_id, text_id, date),
    CONSTRAINT fk_votes_text_final FOREIGN KEY (final_vote_id)
        REFERENCES project.vote_value (vote_id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION,
    CONSTRAINT fk_votes_text_intention FOREIGN KEY (intention_vote_id)
        REFERENCES project.vote_value (vote_id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS project.votes
    OWNER to postgres;

GRANT SELECT ON TABLE project.votes TO PUBLIC;

GRANT ALL ON TABLE project.votes TO postgres;

COMMENT ON TABLE project.votes
    IS 'votes of each parliamentarian for each text for a given date';

COMMENT ON CONSTRAINT fk_votes_text_final ON project.votes
    IS 'Correspond to the vote taken into account';
COMMENT ON CONSTRAINT fk_votes_text_intention ON project.votes
    IS 'Corresponds to the intention of vote. A first vote before it is rectified.';
