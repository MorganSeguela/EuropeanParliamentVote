/*
    Version: V1.1
    Author: Morgan Séguéla
    Date: 01/06/2023
*/

/* Creating view to retrieve more data and optimise DB access */
CREATE OR REPLACE VIEW project.access_vote_content AS    
    SELECT DISTINCT(vc.content_id) as amdt_id, 
        DATE(vc.vote_time) || ' - ' ||LEFT(vc.description, 100) as amdt_sum,
        vc.vote_time as vote_time,
        te.text_id,
        te.text_sum,
        te.text_desc,
        te.text_url,
        vc.description as amdt_desc,
        mn.minute_url as minute_url
    FROM project.vote_content vc,
    project.votes v,
    project.minute mn,
	( 
		(SELECT vc2.content_id, 
		 		te.reference AS text_id,
    			((te.reference::text || ' - '::text) || "left"(te.description, 120)) || '...'::text AS text_sum,
    			te.description AS text_desc,
    			te.url AS text_url
			FROM project.vote_content vc2, project.text te
			WHERE te.reference = vc2.reference_text)
	UNION
		(SELECT vc3.content_id, 
		 		NULL as text_id,
		 		NULL as text_sum,
		 		NULL as text_desc,
		 		NULL as text_url
		 	FROM project.vote_content vc3
		 	WHERE vc3.reference_text IS NULL)
	) te
  WHERE te.content_id = vc.content_id 
        AND  vc.content_id = v.content_id
        AND mn.minute_id = vc.minute_id
    ORDER BY vc.vote_time DESC
;
    
ALTER TABLE project.access_vote_content
    OWNER TO postgres;
COMMENT ON VIEW project.access_vote_content
    IS 'Retrieve all vote content for a given date and the filter will be done in R';

GRANT SELECT ON TABLE project.access_vote_content TO PUBLIC;
GRANT ALL ON TABLE project.access_vote_content TO postgres;
