-- Retrieve seat graph data 
CREATE VIEW project.parliamentarian_seat_graph
AS
SELECT seat_id, cast(seat_xpos as DECIMAL)/cast(square_size_x as DECIMAL) as xpos01,
	-1 * cast(seat_ypos as DECIMAL)/cast(square_size_y as DECIMAL) as ypos01, 
	parliament_name, seat.use
FROM project.seat, project.parliament
WHERE seat.parliament_id = parliament.parliament_id;

ALTER TABLE project.parliamentarian_seat_graph
    OWNER TO postgres;
COMMENT ON VIEW project.parliamentarian_seat_graph
    IS 'Retrieve seats for a graph';

-- Retrieve parliamentarian information    
CREATE OR REPLACE VIEW project.parliamentarian_info
 AS
 SELECT so.parliamentarian_id,
    parl.p_fullname,
    npg.npg_name,
    pg.pg_name,
    parl.country_name,
    so.seat_id
   FROM project.parliamentarian parl,
    project.national_political_group npg,
    project.political_group pg,
    ( SELECT so_1.parliamentarian_id,
            so_1.seat_id
           FROM project.sits_on so_1,
            ( SELECT sits_on.parliamentarian_id,
                    max(sits_on.date) AS recent_date
                   FROM project.sits_on
                  GROUP BY sits_on.parliamentarian_id) sodate
          WHERE so_1.date = sodate.recent_date AND so_1.parliamentarian_id = sodate.parliamentarian_id) so
  WHERE parl.npg_id = npg.npg_id AND parl.pg_id = pg.pg_id AND so.parliamentarian_id = parl.parliamentarian_id;

ALTER TABLE project.parliamentarian_info
    OWNER TO postgres;
COMMENT ON VIEW project.parliamentarian_info
    IS 'Retrieve information about parliamentarian';
