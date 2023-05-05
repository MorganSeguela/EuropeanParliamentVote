-- Retrieve seat graph data 
CREATE OR REPLACE VIEW project.parliament_seat_graph
 AS
 SELECT seat.seat_id,
    seat.seat_xpos::numeric / seat.square_size_x::numeric AS xpos01,
    '-1'::integer::numeric * seat.seat_ypos::numeric / seat.square_size_y::numeric AS ypos01,
    parliament.parliament_name,
    seat.use
   FROM project.seat,
    project.parliament
  WHERE seat.parliament_id = parliament.parliament_id;
  
ALTER TABLE project.parliamentarian_seat_graph
    OWNER TO postgres;
COMMENT ON VIEW project.parliamentarian_seat_graph
    IS 'Retrieve seats for a graph';

GRANT SELECT ON TABLE project.parliament_seat_graph TO PUBLIC;
GRANT ALL ON TABLE project.parliament_seat_graph TO postgres;

    
-- Retrieve parliamentarian information    
CREATE OR REPLACE VIEW project.parliamentarian_info
 AS
 SELECT so.parliamentarian_id,
    parl.p_fullname,
    npg.npg_name,
    pg.pg_name,
    ct.country_name,
    so.seat_id,
    so.date_sit
   FROM project.parliamentarian parl,
    project.national_political_group npg,
    project.political_group pg,
    project.country ct,
    project.sits_on so
  WHERE parl.npg_id = npg.npg_id AND parl.pg_id = pg.pg_id AND so.parliamentarian_id = parl.parliamentarian_id AND ct.country_id = parl.country_id;

ALTER TABLE project.parliamentarian_info
    OWNER TO postgres;
COMMENT ON VIEW project.parliamentarian_info
    IS 'Retrieve information about parliamentarian';

GRANT SELECT ON TABLE project.parliamentarian_info TO PUBLIC;
GRANT ALL ON TABLE project.parliamentarian_info TO postgres;
