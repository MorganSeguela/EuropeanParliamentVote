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

    # Application title
    titlePanel("European Parliament Votes"),
    
    checkboxInput("text_asso", "Vote associated to text ?", value = FALSE),

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
    )
    
)

# Define server logic required to draw a histogram
server <- function(input, output, session) {
    output$choice_text_red = renderUI({
        textData = retrieve_text()
        selectInput("text_id",
                    label = "Choose which text",
                    choices = textData[,2],
                    selected = textData[1,2],
                    multiple = FALSE
        )
    })
    
    
    output$choice_cont_id = renderUI({
        textData = retrieve_text()
        contData = retrieve_content("", FALSE)
        if(input$text_asso){
            contData = retrieve_content(textData[input$text_id == textData[,2],1], input$text_asso)
        }
        print(contData)
        selectInput(
            "content_id",
            label = "Choose which content",
            choices = contData[,2],
            selected = contData[1,2],
            multiple = FALSE
        )
    })
    
    
    output$parlPlot = renderPlotly({
        textData = retrieve_text()
        contData = retrieve_content("", FALSE)
        if(input$text_asso){
            contData = retrieve_content(textData[input$text_id == textData[,2],1], input$text_asso)
        }
        seat_data = get_seat()
        vote_trans = get_vote_val()
        
        cont_id_parl = choose_parliament(contData[input$content_id == contData[,2],1])
        
        vote_result = get_result(contData[input$content_id == contData[,2],1])
        
        remove(textData, contData)
        
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
        vote_trans$color = c("blue", "red", "darkgrey", "black")
        cur_vote = merge(cur_vote, vote_trans, by.x = "final_vote_id", by.y = "vote_id")
        
        cur_vote = cur_vote[,c(1:6,8:12,15:17)]
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
        
        parliament_graph
        
        plot_v1 = ggplotly(parliament_graph, originalData = TRUE)
        
        to_modify_plot = plotly_build(plot_v1)
        
        for (i in c(1:length(to_modify_plot$x$data))) {
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
    
    output$text_desc = renderUI({
        textData = retrieve_text()
        cur_text = textData[input$text_id == textData[,2],]
        remove(textData)
        HTML(paste("Reference: ", cur_text[1],
                   "<br />Description:<br />", cur_text[3],
                   "<br />Available here: ", cur_text[4]))
    })
    
    output$cont_desc = renderUI({
        textData = retrieve_text()
        contData = retrieve_content("", FALSE)
        if(input$text_asso){
            contData = retrieve_content(textData[input$text_id == textData[,2],1], input$text_asso)
        }
        cur_cont = contData[input$content_id == contData[,2],]
        print(cur_cont)
        remove(contData)
        HTML(paste("This vote is about: ", cur_cont[4],
                   "<br />The minute is available here: ", cur_cont[5]))
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