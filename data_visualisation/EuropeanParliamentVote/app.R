#
# This is a Shiny web application. You can run the application by clicking
# the 'Run App' button above.
#
# Find out more about building applications with Shiny here:
#
#    http://shiny.rstudio.com/
#

library(shiny)

library(DBI)
library(pool)

library(ConfigParser)
library(RPostgreSQL)

library(ggplot2)
library(plotly)

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

onStop(function() {
    cat("closing db connections")
    poolClose(cur_pool)
})

# Define UI for application that draws a histogram
ui <- fluidPage(
        
    # Application title
    titlePanel("European Parliament Votes"),
    
    
    sidebarPanel(
        uiOutput("choice_text_id")
    ),
    
        # Show a plot of the generated distribution
        mainPanel(
            # plotOutput("distPlot")
            plotlyOutput("parlPlot"),
            htmlOutput("description")
        )
)

# Define server logic required to draw a histogram
server <- function(input, output) {
    
    
    
    
    sqlOutput = reactive({
        new_con = poolCheckout(cur_pool)
        input_text_id = "SELECT text_id FROM \"project_V01\".text;"
        query = sqlInterpolate(new_con, input_text_id)
        resData = dbGetQuery(new_con, input_text_id)
        poolReturn(new_con)
        resData
    })

    output$choice_text_id = renderUI({
        selectInput(
            "text_id",
            label = "Choose which text ID",
            choices = sqlOutput(),
            selected = max(sqlOutput()),
            multiple = FALSE
        )
    })
    
    output$parlPlot = renderPlotly({
        new_con = poolCheckout(cur_pool)
        
        seat_query = "SELECT *
                FROM project.parliamentarian_seat_graph
                WHERE UPPER(use) LIKE 'PARLIAMENTARIAN'
                ;"
        
        seat_data = dbGetQuery(new_con, seat_query)

        vote_trans_query = "SELECT * FROM project.vote_value;"
        vote_trans = dbGetQuery(new_con, vote_trans_query)
        
        if(is.null(input$text_id)){
            input$text_id = 153633 
        }
        print(input)
        vote_query = paste("SELECT *
            FROM project.votes
            WHERE text_id = ", input$text_id, ";")
        print(vote_query)
        vote_data = dbGetQuery(new_con, vote_query)

        parl_query = paste("SELECT *
            FROM project.parliamentarian_info
            WHERE date = '", vote_data$date[1],"';", sep="")

        parl_data = dbGetQuery(new_con, parl_query)
        poolReturn(new_con)
        

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
    })
    
    output$description = renderUI({
        new_con = poolCheckout(cur_pool)
        text_query = paste("SELECT * FROM project.text WHERE text_id = ", input$text_id, ";")
        text_data = dbGetQuery(new_con, text_query)
        poolReturn(new_con)
        
        HTML(paste("Reference: ", text_data$reference,
              "<br />Description:<br />", text_data$description,
              "<br />Available here: ", text_data$url))
    })
    
}

# Run the application 
shinyApp(ui = ui, server = server)
