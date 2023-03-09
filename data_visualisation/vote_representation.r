require("RPostgreSQL")
require("ConfigParser")

require("ggplot2")
require("plotly")

setwd("~/Documents/EuropeanParliamentVote/")

config_db <- ConfigParser$new(Sys.getenv(), optionxform = identity)
config_db$read("../EP_project/data_storage/database.ini")
config_db$data$postgresql

drv = dbDriver("PostgreSQL")
con = dbConnect(drv = drv,
                dbname = config_db$data$postgresql$database,
                host = config_db$data$postgresql$host,
                port = 5432,
                user = config_db$data$postgresql$user,
                password = config_db$data$postgresql$password)

seat_query = "SELECT *
                FROM project.parliamentarian_seat_graph
                WHERE UPPER(use) LIKE 'PARLIAMENTARIAN'
                ;"
seat_data = dbGetQuery(con, seat_query)

vote_trans_query = "SELECT * FROM project.vote_value;"
vote_trans = dbGetQuery(con, vote_trans_query)

vote_query = "SELECT *
    FROM project.votes
    WHERE text_id = (SELECT MAX(text_id) FROM project.votes);"

vote_data = dbGetQuery(con, vote_query)

parl_query = paste("SELECT * 
    FROM project.parliamentarian_info
    WHERE date = '", vote_data$date[1],"';", sep="")

parl_data = dbGetQuery(con, parl_query)

text_query = "SELECT * FROM project.text;"
text_data = dbGetQuery(con, text_query)

tmp_parl_place = merge(seat_data, parl_data, by = "seat_id", all.x=TRUE)

cur_vote = merge(tmp_parl_place, vote_data, by = "parliamentarian_id", all.x = TRUE)
cur_vote$final_vote_id[is.na(cur_vote$final_vote_id)] = 3

cur_vote$parliament_name[is.na(cur_vote$parliamentarian_id)] = "unknown"

vote_trans = rbind(vote_trans, c(3, "absent", 0))
cur_vote = merge(cur_vote, vote_trans, by.x = "final_vote_id", by.y = "vote_id")
cur_vote = cur_vote[,c(1:6,8:12,16:17)]
cur_vote$final_vote_id = factor(cur_vote$final_vote_id)

parliament_graph = ggplot(cur_vote) +
    geom_point(mapping = aes(x=xpos01, y=ypos01, color=final_vote_id)) +
    scale_color_manual(
        labels = unique(cur_vote$vote_name),
        values = c("blue", "red", "darkgrey", "black"),
        guide = guide_legend(
        title = "vote",
        title.position = "top",
        title.hjust = 0.5,
        title.vjust = 0.1,
        direction = "horizontal"
    )) +
    theme_void() +
    theme(legend.position = "bottom")

plot_v1 = ggplotly(parliament_graph, originalData = TRUE)

to_modify_plot = plotly_build(plot_v1)


for (i in c(1:4)) {
    to_modify_plot$x$data[[i]]$text = paste(cur_vote$p_fullname[cur_vote$final_vote_id == i-1], "<br />",
                                            cur_vote$pg_name[cur_vote$final_vote_id == i-1], "<br />", 
                                            cur_vote$country_name[cur_vote$final_vote_id == i-1])
    to_modify_plot$x$data[[i]]$name = unique(cur_vote$vote_name)[i]
}

to_modify_plot %>%
    layout(
        xaxis = list(zeroline = F, showgrid = F),
        yaxis = list(zeroline = F, showgrid = F),
        legend = list(orientation = "h",
                      title = list(side = "top"))
    )

str(to_modify_plot$x$data[[1]])

unique(cur_vote$vote_name)