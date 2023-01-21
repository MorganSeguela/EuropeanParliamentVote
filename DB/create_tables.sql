/*
    -- EUROPEAN PARLIAMENT PROJECT DB --

Author: Morgan Séguéla

Version:
    V0.1: First creation and local implementation
*/

-- DROP TABLE IF EXISTS project.votes;

-- DROP TABLE IF EXISTS project."Parliamentarian";
-- DROP TABLE IF EXISTS project."PoliticGroup";
-- DROP TABLE IF EXISTS project."NationalPoliticalGroup";

-- DROP TABLE IF EXISTS project."Text";
-- DROP TABLE IF EXISTS project."VoteValue";

-- DROP TABLE IF EXISTS project."Seat";
-- DROP TABLE IF EXISTS project."Parliament";


-- Table: project.PoliticGroup
CREATE TABLE IF NOT EXISTS project."PoliticGroup"
(
    pg_id integer NOT NULL,
    pg_name character varying(128) COLLATE pg_catalog."default" NOT NULL,
    CONSTRAINT pk_politicalgroup PRIMARY KEY (pg_id)
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS project."PoliticGroup"
    OWNER to postgres;

GRANT SELECT ON TABLE project."PoliticGroup" TO PUBLIC;

GRANT ALL ON TABLE project."PoliticGroup" TO postgres;

COMMENT ON TABLE project."PoliticGroup"
    IS 'Politic group inside the parliament in which the parliamentarian is.';

-- Table: project.NationalPoliticalGroup
CREATE TABLE IF NOT EXISTS project."NationalPoliticalGroup"
(
    npg_id integer NOT NULL,
    npg_name character varying(128) COLLATE pg_catalog."default" NOT NULL,
    CONSTRAINT pk_npg PRIMARY KEY (npg_id)
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS project."NationalPoliticalGroup"
    OWNER to postgres;

GRANT SELECT ON TABLE project."NationalPoliticalGroup" TO PUBLIC;

GRANT ALL ON TABLE project."NationalPoliticalGroup" TO postgres;

COMMENT ON TABLE project."NationalPoliticalGroup"
    IS 'Represent the national political group of the parliamentarian';


-- Table: project.VoteValue
CREATE TABLE IF NOT EXISTS project."VoteValue"
(
    vote_id integer NOT NULL,
    vote_name character varying(16) COLLATE pg_catalog."default" NOT NULL,
    vote_value integer NOT NULL,
    CONSTRAINT pk_votevalue PRIMARY KEY (vote_id)
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS project."VoteValue"
    OWNER to postgres;

GRANT SELECT ON TABLE project."VoteValue" TO PUBLIC;

GRANT ALL ON TABLE project."VoteValue" TO postgres;

COMMENT ON TABLE project."VoteValue"
    IS 'Value of choices during votes : abstention, for, against, missing';

-- Table: project.Text
CREATE TABLE IF NOT EXISTS project."Text"
(
    text_id integer NOT NULL,
    reference character varying(16) COLLATE pg_catalog."default" NOT NULL,
    description text COLLATE pg_catalog."default",
    url character varying(256) COLLATE pg_catalog."default" NOT NULL,
    CONSTRAINT pk_text PRIMARY KEY (text_id)
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS project."Text"
    OWNER to postgres;

GRANT SELECT ON TABLE project."Text" TO PUBLIC;

GRANT ALL ON TABLE project."Text" TO postgres;

COMMENT ON TABLE project."Text"
    IS 'Text submitted to parliamentarian votes.';

-- Table: project.Parliament
CREATE TABLE IF NOT EXISTS project."Parliament"
(
    parliament_id integer NOT NULL,
    parliament_name character varying(16) COLLATE pg_catalog."default" NOT NULL,
    parliament_abr character varying(3) COLLATE pg_catalog."default" NOT NULL,
    CONSTRAINT pk_parliament PRIMARY KEY (parliament_id)
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS project."Parliament"
    OWNER to postgres;

GRANT SELECT ON TABLE project."Parliament" TO PUBLIC;

GRANT ALL ON TABLE project."Parliament" TO postgres;

COMMENT ON TABLE project."Parliament"
    IS 'Parliament, correspond to Brussels or Strasbourg';


-- Table: project.Seat
CREATE TABLE IF NOT EXISTS project."Seat"
(
    seat_id integer NOT NULL,
    seat_xpos integer NOT NULL,
    seat_ypos integer NOT NULL,
    square_size integer NOT NULL,
    use character varying(16) COLLATE pg_catalog."default" NOT NULL,
    parliament_id integer NOT NULL,
    CONSTRAINT pk_seat PRIMARY KEY (seat_id),
    CONSTRAINT fk_seat_parliament FOREIGN KEY (parliament_id)
        REFERENCES project."Parliament" (parliament_id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS project."Seat"
    OWNER to postgres;

GRANT SELECT ON TABLE project."Seat" TO PUBLIC;

GRANT ALL ON TABLE project."Seat" TO postgres;

COMMENT ON TABLE project."Seat"
    IS 'Seat where parliamentarian is on';

-- Table: project.Parliamentarian
CREATE TABLE IF NOT EXISTS project."Parliamentarian"
(
    parliamentarian_id integer NOT NULL,
    p_name character varying(64) COLLATE pg_catalog."default",
    p_surname character varying(128) COLLATE pg_catalog."default",
    country_name character varying(128) COLLATE pg_catalog."default",
    npg_id integer,
    pg_id integer,
    CONSTRAINT pk_parliamentarian PRIMARY KEY (parliamentarian_id),
    CONSTRAINT fk_parliamentarian_npg FOREIGN KEY (npg_id)
        REFERENCES project."NationalPoliticalGroup" (npg_id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION,
    CONSTRAINT fk_parliamentarian_pg FOREIGN KEY (pg_id)
        REFERENCES project."PoliticGroup" (pg_id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS project."Parliamentarian"
    OWNER to postgres;

GRANT SELECT ON TABLE project."Parliamentarian" TO PUBLIC;

GRANT ALL ON TABLE project."Parliamentarian" TO postgres;

COMMENT ON TABLE project."Parliamentarian"
    IS 'Member of parliamentary';

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
        REFERENCES project."VoteValue" (vote_id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION,
    CONSTRAINT fk_votes_text_intention FOREIGN KEY (intention_vote_id)
        REFERENCES project."VoteValue" (vote_id) MATCH SIMPLE
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