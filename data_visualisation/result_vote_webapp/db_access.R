
library(DBI)
library(pool)

library(ConfigParser)
library(RPostgreSQL)

setwd("~/Documents/EuropeanParliamentVote/")

config_db <- ConfigParser$new(Sys.getenv(), optionxform = identity)
config_db$read("../EP_project/data_storage/database.ini")
config_db$data$postgresql

drv = dbDriver("PostgreSQL")
cur_pool = dbPool(
    drv = drv,
    dbname = config_db$data$postgresql$database,
    host = config_db$data$postgresql$host,
    port = 5432,
    user = config_db$data$postgresql$user,
    password = config_db$data$postgresql$password
)



retrieve_content = function(reference, isText=TRUE){
    new_con = poolCheckout(cur_pool)
    input_text_id = "
        SELECT DISTINCT(vc.content_id) as id, DATE(vote_time) || ' - ' || LEFT(description, 100) as desc
        FROM project.vote_content vc, project.votes v
        WHERE reference_text IS NULL
        AND vc.content_id = v.content_id;
    "
    
    print(isText)
    print(reference)
    
    if(isText && reference != ""){
        input_text_id = paste("
        SELECT DISTINCT(vc.content_id) as id, DATE(vote_time) || ' - ' || LEFT(description, 100) as desc
        FROM project.vote_content vc, project.votes v
        WHERE vc.content_id = v.content_id
        AND reference_text LIKE \'", reference,"\';", sep="")
    }
    
    print(input_text_id)

    query = sqlInterpolate(new_con, input_text_id)
    resData = dbGetQuery(new_con, input_text_id)
    poolReturn(new_con)
    resData
}



retrieve_text = function(){
    new_con = poolCheckout(cur_pool)
    input_text_id = "
            SELECT DISTINCT(reference) as id, reference || ' - ' || LEFT(description, 120) || '...' as desc
            FROM project.text t, project.vote_content vc, project.votes v
            WHERE t.reference = vc.reference
            AND vc.content_id = v.content_id;
    "
    query = sqlInterpolate(new_con, input_text_id)
    resData = dbGetQuery(new_con, input_text_id)
    poolReturn(new_con)
    resData
}


