
library(DBI)
library(pool)

library(ConfigParser)
library(RPostgreSQL)

setwd("~/Documents/EuropeanParliamentVote/")

config_db <- ConfigParser$new(Sys.getenv(), optionxform = identity)
config_db$read("database.ini")
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
        SELECT DISTINCT(vc.content_id) as id,
            DATE(vote_time) || ' - ' || LEFT(description, 100) as desc,
            vote_time,
            vc.description,
            mn.minute_url
        FROM project.vote_content vc, project.votes v, project.minute mn
        WHERE reference_text IS NULL
        AND vc.content_id = v.content_id
        AND vc.minute_id = mn.minute_id
        ORDER BY vote_time DESC;
    "
    
    if(isText && !is.na(reference)){
        input_text_id = paste("
        SELECT DISTINCT(vc.content_id) as id,
            DATE(vote_time) || ' - ' || LEFT(description, 100) as desc,
            vote_time,
            vc.description,
            mn.minute_url
        FROM project.vote_content vc, project.votes v, project.minute mn
        WHERE vc.content_id = v.content_id
        AND vc.minute_id = mn.minute_id
        AND reference_text LIKE \'", reference,"\'
                              ORDER BY vote_time DESC;", sep="")
    }

    query = sqlInterpolate(new_con, input_text_id)
    resData = dbGetQuery(new_con, input_text_id)
    poolReturn(new_con)
    resData
}



retrieve_text = function(){
    new_con = poolCheckout(cur_pool)
    input_text_id = "
        SELECT DISTINCT(te.reference) as id,
            te.reference || ' - ' || LEFT(te.description, 120) || '...' as desc,
            te.description,
            te.url
        FROM project.text te, project.vote_content vc, project.votes v
        WHERE te.reference = vc.reference_text
        AND vc.content_id = v.content_id;
    "
    query = sqlInterpolate(new_con, input_text_id)
    resData = dbGetQuery(new_con, input_text_id)
    poolReturn(new_con)
    resData
}


get_seat = function(){
    new_con = poolCheckout(cur_pool)
    seat_query = "SELECT *
                FROM project.parliament_seat_graph
                WHERE UPPER(use) LIKE 'PARLIAMENTARIAN'
                ;"
    query = sqlInterpolate(new_con, seat_query)
    resData = dbGetQuery(new_con, seat_query)
    poolReturn(new_con)
    resData
}


choose_parliament = function(content_id){
    this_id = 152544
    
    if(length(content_id) != 0){
        this_id = content_id
    }
    
    first_part= "
        SELECT pl.parliament_name as pname, so.date_sit as max_date_seat, count(so.parliamentarian_id) as nb
        FROM project.votes v, project.sits_on so, project.seat s, project.parliament pl
        WHERE content_id = "
    second_part = "
        AND v.parliamentarian_id = so.parliamentarian_id
        AND so.seat_id = s.seat_id
        AND s.parliament_id = pl.parliament_id
        GROUP BY pl.parliament_name, so.date_sit
        ORDER BY nb DESC, max_date_seat DESC
        LIMIT 1;
    "
    choose_query = paste(first_part, this_id, second_part, sep="")
    new_con = poolCheckout(cur_pool)
    query = sqlInterpolate(new_con, choose_query)
    resData = dbGetQuery(new_con, choose_query)
    poolReturn(new_con)
    resData
}


get_vote_val = function(){
    vote_trans_query = "SELECT * FROM project.vote_value;"
    new_con = poolCheckout(cur_pool)
    query = sqlInterpolate(new_con, vote_trans_query)
    resData = dbGetQuery(new_con, vote_trans_query)
    poolReturn(new_con)
    resData
}


get_result = function(content_id){
    this_id = 152544
    
    if(length(content_id) != 0){
        this_id = content_id
    }
    
    result_query = paste("SELECT *
            FROM project.votes
            WHERE content_id = ", this_id, ";")
    new_con = poolCheckout(cur_pool)
    query = sqlInterpolate(new_con, result_query)
    resData = dbGetQuery(new_con, result_query)
    poolReturn(new_con)
    resData
}

get_parl_info = function(chosen_date){
    this_date = "2023-03-13"
    if(!is.na(chosen_date)){
        this_date = chosen_date
    }
    parl_query = paste("SELECT *
            FROM project.parliamentarian_info
            WHERE date_sit = '", chosen_date,"';", sep="")
    new_con = poolCheckout(cur_pool)
    query = sqlInterpolate(new_con, parl_query)
    resData = dbGetQuery(new_con, parl_query)
    poolReturn(new_con)
    resData
}

get_text_info = function(text_ref){
    
}

clean_con = function(){
    print(cur_pool)
    poolClose(cur_pool)
}

