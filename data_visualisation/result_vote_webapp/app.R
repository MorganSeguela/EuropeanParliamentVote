#
# This is a Shiny web application. You can run the application by clicking
# the 'Run App' button above.
#
# Find out more about building applications with Shiny here:
#
#    http://shiny.rstudio.com/
#

library(shiny)

library(ggplot2)
library(plotly)


source("db_access.R", local=T)

# Define UI for application that draws a histogram
ui <- fluidPage(
    includeCSS("style.css"),
    
    # Application title
    HTML("<body>
            <div class=\"main\">
                <div class=\"content\">"),
    
    HTML("<h2>European Parliament Votes</h2>
          <div class=\"clr\"></div>" ),
    
    fluidRow(
        column(width = 4,
               uiOutput("choice_date")),
        column(width = 4,
               checkboxInput(
                   "text_asso",
                   "Vote associated to text ?",
                   value = FALSE))
    ),
    
    fluidRow(
        conditionalPanel(
            condition="input.text_asso == true",
            column(4,
                   uiOutput("choice_text_red")
                   )
               ),
        column(4,
               uiOutput("choice_cont_id")
               )
    ),

    mainPanel(
        plotlyOutput("parlPlot"),
        conditionalPanel(
            condition = "input.text_asso == true",
            htmlOutput("text_desc")
        ),
        htmlOutput("cont_desc")
    ),
    HTML("      <div class=\"clr\"></div>
                </div>
            </div>
         </body>")
)

# Define server logic required to draw a histogram
server <- function(input, output, session) {
    output$choice_date = renderUI({
        dateData = retrieve_date()
        selectInput("date_votes",
                    label = "When did the vote happen ?",
                    choices = dateData,
                    selected = dateData[1],
                    multiple = FALSE
                   )    
    })
    
    output$choice_text_red = renderUI({
        retrieve_text_amd(input$date_votes)
        selectInput("text_id",
                    label = "Choose which text",
                    choices = unique(glob_text_amdt_df$text_sum[!is.na(glob_text_amdt_df$text_id)]),
                    selected = glob_text_amdt_df$text_sum[!is.na(glob_text_amdt_df$text_id)][1],
                    multiple = FALSE
        )
    })
    
    
    output$choice_cont_id = renderUI({
        retrieve_text_amd(input$date_votes)
        contData = NULL
        if(input$text_asso){
            print(glob_text_amdt_df[glob_text_amdt_df$text_sum == input$text_id,])
            contData = glob_text_amdt_df[glob_text_amdt_df$text_sum == input$text_id &
                                             !is.na(glob_text_amdt_df$text_sum),]
        } else {
            print(glob_text_amdt_df[is.na(glob_text_amdt_df$text_id),])
            contData = glob_text_amdt_df[is.na(glob_text_amdt_df$text_id),]
        }
        selectInput(
            "content_id",
            label = "Choose which content",
            choices = contData$amdt_sum,
            selected = contData$amdt_sum[1],
            multiple = FALSE
        )
    })
    
    
    output$parlPlot = renderPlotly({
        contData = glob_text_amdt_df[glob_text_amdt_df$amdt_sum == input$content_id,]
        
        seat_data = glob_seat_data
        vote_trans = glob_vote_value
        
        cont_id_parl = choose_parliament(contData$amdt_id)
        
        vote_result = get_result(contData$amdt_id)
        
        remove(contData)
        
        print(cont_id_parl)
        
        parl_info = get_parl_info(cont_id_parl[,2])
    
        cur_seat = seat_data[seat_data$parliament_name == cont_id_parl$pname,]
        
        tmp_parl_place = merge(cur_seat, parl_info, by = "seat_id", all.x=TRUE)
        remove(seat_data, cont_id_parl)
        gc()
        
        cur_vote = merge(tmp_parl_place, vote_result, by = "parliamentarian_id", all.x = TRUE)
        cur_vote$final_vote_id[is.na(cur_vote$final_vote_id)] = 3
        
        cur_vote$parliament_name[is.na(cur_vote$parliamentarian_id)] = "unknown"
        vote_trans = rbind(vote_trans, c(3, "absent", 0))
        vote_trans$color = c("#40FF40", "#FF4040", "#8c8c8c", "#000000")
        vote_trans$point = c("cross-thin","line-ew","diamond-tall", "circle")
        cur_vote = merge(cur_vote, vote_trans, by.x = "final_vote_id", by.y = "vote_id")

        cur_vote = cur_vote[,c(1:6,8:12,15:18)]
        cur_vote$final_vote_id = factor(cur_vote$final_vote_id, levels = vote_trans$vote_id)
        
        
        parliament_graph = ggplot(cur_vote) +
            geom_point(mapping = aes(x=xpos01, y=ypos01, color=final_vote_id)) +
            scale_color_manual(
                labels = unique(cur_vote$vote_name),
                values = unique(cur_vote$color),
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
        
        to_modify_plot = plotly_build(plot_v1) %>% 
            layout(
                    xaxis = list(fixedrange = TRUE),
                    yaxis = list(fixedrange = TRUE)
                )
        
        
        for (i in c(1:length(to_modify_plot$x$data))) {
            to_modify_plot$x$data[[i]]$text = paste(cur_vote$p_fullname[cur_vote$final_vote_id == i-1], "<br />",
                                                    cur_vote$pg_name[cur_vote$final_vote_id == i-1], "<br />", 
                                                    cur_vote$country_name[cur_vote$final_vote_id == i-1])
            to_modify_plot$x$data[[i]]$name = unique(cur_vote$vote_name)[i]
            to_modify_plot$x$data[[i]]$marker$symbol = unique(cur_vote$point)[i]
            
        }
        
        to_modify_plot %>%
            layout(
                xaxis = list(zeroline = F, showgrid = F),
                yaxis = list(zeroline = F, showgrid = F),
                legend = list(orientation = "h",
                              title = list(side = "top"))
            )
    })
    
    output$text_desc = renderUI({
        cur_text = glob_text_amdt_df[glob_text_amdt_df$text_sum == input$text_id,]
        HTML(paste("<div class=\"article\">
                    <h2> Text Information </h2>
                    <div class=\"clr\"></div>
                    Reference: ", cur_text$text_id[1],
                   "<br />Description:<br />", cur_text$text_desc[1],
                   "<br />Available here: <a href=\"", cur_text$text_url[1],
                   "\">", cur_text$text_url[1], "</a></div>"))
    })
    
    output$cont_desc = renderUI({
        cur_cont = glob_text_amdt_df[glob_text_amdt_df$amdt_sum == input$content_id,]
        HTML(paste("<div class=\"article\">
                    <h2>Vote content</h2>
                    <div class=\"clr\"></div>
                    This vote is about: ", cur_cont$amdt_desc,
                    "<br />The minute is available here: <a href=\"", cur_cont$minute_url,
                    "\">", cur_cont$minute_url,"</a></div>"))
    })
}

# Run the application 
shinyApp(
    ui = ui,
    server = server,
    onStart = function() {
        cat("Doing application setup\n")
        
        onStop(function() {
            cat("Doing application cleanup\n")
            clean_con()
        })
    }
)
