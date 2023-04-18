#
# This is a Shiny web application. You can run the application by clicking
# the 'Run App' button above.
#
# Find out more about building applications with Shiny here:
#
#    http://shiny.rstudio.com/
#

library(shiny)
source("db_access.R", local=T)

# Define UI for application that draws a histogram
ui <- fluidPage(

    # Application title
    titlePanel("European Parliament Votes"),
    
    checkboxInput("text_asso", "Vote associated to text ?", value = FALSE),

    sidebarPanel(
        conditionalPanel(
            condition="input.text_asso == true",
            uiOutput("choice_text_red")
        ),
        uiOutput("choice_cont_id")
    ),
    
    # Sidebar with a slider input for number of bins 
    sidebarLayout(
        sidebarPanel(
            sliderInput("bins",
                        "Number of bins:",
                        min = 1,
                        max = 50,
                        value = 30)
        ),

        # Show a plot of the generated distribution
        mainPanel(
           plotOutput("distPlot")
        )
    )
)

# Define server logic required to draw a histogram
server <- function(input, output) {
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
        print("ok")
        contData = retrieve_content("", FALSE)
        print("lol")
        if(input$text_asso){
            print(input$text_id)
            print(textData[input$text_id == textData[,2],1])
            contData = retrieve_content(textData[input$text_id == textData[,2],1], input$text_asso)
        }
        selectInput(
            "content_id",
            label = "Choose which content",
            choices = contData[,2],
            selected = contData[1,2],
            multiple = FALSE
        )
    })
    
    
    output$distPlot <- renderPlot({
        # generate bins based on input$bins from ui.R
        x    <- faithful[, 2]
        bins <- seq(min(x), max(x), length.out = input$bins + 1)

        # draw the histogram with the specified number of bins
        hist(x, breaks = bins, col = 'darkgray', border = 'white',
             xlab = 'Waiting time to next eruption (in mins)',
             main = 'Histogram of waiting times')
    })
}

# Run the application 
shinyApp(ui = ui, server = server)
