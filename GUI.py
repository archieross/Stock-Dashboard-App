from tkinter import *
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from API_Call_AlphaVantage import GetCandleChart, GetNewsData
from API_Call_Twitter import GetTweets
import webbrowser
from TimeScript import ConvertTimestamp

root = Tk()


root.config(bg='navy')
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

#Set the window size to fill the screen
root.geometry(f"{screen_width}x{screen_height}")

##########################################

def InitialPage():

    welcomeFrame = Frame(root, padx=20, pady=20)
    welcomeFrame.grid_rowconfigure(1, weight=2, uniform="equal")
    welcomeFrame.grid_rowconfigure(2, weight=5, uniform="equal")
    welcomeFrame.grid_rowconfigure(3, weight=2, uniform="equal")
    welcomeFrame.grid_rowconfigure(4, weight=2, uniform="equal")
    welcomeFrame.place(relx=0.5, rely=0.5, anchor="center")  #Center the frame


    welcomeLabel = Label(welcomeFrame,font=("Helvetica", 20), text="Welcome to the Stock Analyser Program!\nPlease use a 'Ticker Symbol' to search for a stock.", fg = 'navy')
    searchBox = Entry(welcomeFrame, bg='white')
    searchButton = Button(welcomeFrame, text='Search',bg='navy', command=lambda: LookupStock(searchBox.get(), welcomeFrame))


    welcomeLabel.grid(row=1, column= 1)
    searchBox.grid(row=3, column= 1)
    searchButton.grid(row=4, column= 1)

InitialPage()


#########################################################
#Show Stock Report Page


#Helps configure the positions of widgets on the screen
def ConfigureRoot(welcomeFrame):

    if welcomeFrame:
        welcomeFrame.destroy()

    #First we must set the root row and column configurations
    root.config(padx=20, pady=20)
    root.grid_rowconfigure(1, weight=1, uniform="equal") #search
    root.grid_rowconfigure(2, weight=1, uniform="equal") #space
    root.grid_rowconfigure(3, weight=20, uniform="equal") #candle chart and other chart

    root.grid_columnconfigure(1, weight=20, uniform="equal")
    root.grid_columnconfigure(2, weight=1, uniform="equal")
    root.grid_columnconfigure(3, weight=8, uniform="equal")


def PlaceTopRow(ticker):

    topRowFrame = Frame(root)
    topRowFrame.grid_propagate(False)
    topRowFrame.grid(row=1, column=1, columnspan=3, sticky='nsew')
    


    tickerLabel = Label(topRowFrame, text=ticker, font=("Helvetica", 20))
    tickerLabel.pack(side='left')

    searchFrame = Frame(topRowFrame, bg='white')
    searchFrame.pack(side='right')

    searchBox = Entry(searchFrame, bg='white')
    searchButton = Button(searchFrame, text='Search',bg='navy', command=lambda: LookupStock(searchBox.get()))
    searchButton.pack(side='right')
    searchBox.pack(side='right')
    
def GetPublicFrame():

    publicFrame = Frame(root, bg= 'navy')
    publicFrame.grid(row=3, column=3, sticky='nsew')
    publicFrame.grid_rowconfigure(1, weight=8, uniform="equal") #News
    publicFrame.grid_rowconfigure(2, weight=1, uniform="equal") #Space
    publicFrame.grid_rowconfigure(3, weight=6, uniform="equal") #X/Twitter
    publicFrame.grid_columnconfigure(1, weight=1, uniform="equal")

    return publicFrame

#Add the widgets to the screen (charts, tweet, ...)
def BuildReportScreen(reportDict, welcomeFrame):

    ConfigureRoot(welcomeFrame)

    PlaceTopRow(reportDict['ticker'])

    PlaceCandleChart(reportDict)

    publicFrame = GetPublicFrame()

    PlaceNewsFrame(reportDict['stories'], publicFrame, 0)
    PlaceTweetFrame(reportDict['tweets'], publicFrame, 0)

###################################Public Tweets/X######################################
def ChangeTweet(currentIndex, numTweets, direction, tweets, TweetFrame, publicFrame):
    
    TweetFrame.grid_forget()

    if direction == 'forward':
        newIndex = (currentIndex + 1) % numTweets

    elif direction == 'back':
        newIndex = (currentIndex - 1) % numTweets
    
    PlaceTweetFrame(tweets, publicFrame, newIndex)


def PlaceTweetFrame(tweets, publicFrame, index=0):

    TweetFrame = Frame(publicFrame)

    TweetFrame.grid_rowconfigure(0, weight=1, uniform="equal") #Recent Tweets Header

    TweetFrame.grid_rowconfigure(1, weight=1, uniform="equal") #Author
    TweetFrame.grid_rowconfigure(2, weight=1, uniform='equal') #Time
    TweetFrame.grid_rowconfigure(4, weight=3, uniform='equal') #Tweet
    TweetFrame.grid_rowconfigure(5, weight=1, uniform='equal') #Buttons

    TweetFrame.grid_columnconfigure(1, weight=1, uniform='equal')
    TweetFrame.grid_columnconfigure(2, weight=1, uniform='equal')
    TweetFrame.grid(row=3, column=1, sticky='nsew')

    currentTweet = tweets[index]

    Label(TweetFrame, text='Recent Tweets', font=("", 16, "bold")).grid(row=0, column=1, columnspan=2)

    currentAuthor = Text(TweetFrame, wrap='word', height=2, width=40)
    currentAuthor.tag_configure('center', justify='center')  #Create a tag for center alignment
    currentAuthor.insert('1.0', currentTweet.username, 'center')  #Apply the tag when inserting text
    currentAuthor.config(state='disabled')  #Make it read-only
    currentAuthor.grid(row=1, column=1, columnspan=2, sticky='nsew')

    ###

    currentDate = Text(TweetFrame, wrap='word', height=2, width=40)
    currentDate.tag_configure('center', justify='center')  
    currentDate.insert('1.0', ConvertTimestamp(currentTweet.created_at), 'center') 
    currentDate.config(state='disabled') 
    currentDate.grid(row=2, column=1, columnspan=2, sticky='nsew')
    

    ###

    currentText = Text(TweetFrame, wrap='word', height=2, width=40)
    currentText.tag_configure('center', justify='left') 
    currentText.insert('1.0', currentTweet.text, 'left')
    currentText.config(state='disabled')
    currentText.grid(row=4, column=1, columnspan=2, sticky='nsew')

    

    forwardButton = Button(TweetFrame, text="->", command=lambda: ChangeTweet(index, len(tweets), 'forward', tweets, TweetFrame, publicFrame))
    backButton = Button(TweetFrame, text="<-", command=lambda: ChangeTweet(index, len(tweets), 'back', tweets, TweetFrame, publicFrame))

    
    backButton.grid(row=5, column=1, columnspan=1)
    forwardButton.grid(row=5, column=2, columnspan=1)

    pass


##############################News Articles############################################
def OpenURL(url):
    webbrowser.open(url)

def ChangeArticleIndex(currentIndex, numStories, direction, stories, NewsFrame, publicFrame):

    NewsFrame.grid_forget()

    if direction == 'forward':
        newIndex = (currentIndex + 1) % numStories


    elif direction == 'back':
        newIndex = (currentIndex - 1) % numStories
    
    PlaceNewsFrame(stories, publicFrame, newIndex)


def PlaceNewsFrame(stories, publicFrame, index=0 ):

    NewsFrame = Frame(publicFrame)
    NewsFrame.grid_rowconfigure(0, weight=1, uniform="equal") #News Stories (title for user)
    NewsFrame.grid_rowconfigure(1, weight=3, uniform="equal") #Title
    NewsFrame.grid_rowconfigure(2, weight=5, uniform='equal') #Summary
    NewsFrame.grid_rowconfigure(3, weight=1, uniform='equal') #Author
    NewsFrame.grid_rowconfigure(4, weight=1, uniform='equal') #Date
    NewsFrame.grid_rowconfigure(5, weight=1, uniform='equal') #Forward and Back buttons
    NewsFrame.grid_columnconfigure(1, weight=1, uniform='equal')
    NewsFrame.grid_columnconfigure(2, weight=1, uniform='equal')
    NewsFrame.grid(row=1, column=1, sticky='nsew')

    story = stories[index]

    ############

    Label(NewsFrame, text='Recent News Stories', font=("", 16, "bold")).grid(row=0, column=1, columnspan=2)

    ############Title###########

    currentTitle = Text(NewsFrame, wrap='word', height=2, width=40)
    currentTitle.tag_configure('center', justify='center')  #Create a tag for center alignment
    currentTitle.insert('1.0', story['title'], 'center')  #Apply the tag when inserting text
    currentTitle.config(state='disabled')  #Make it read-only
    currentTitle.grid(row=1, column=1, columnspan=2, sticky='nsew')

    #URL Link
    currentTitle.tag_add("full_text_link", "1.0", END)  #Starting at the beginning and spanning to the end
    currentTitle.tag_config("full_text_link", foreground="blue", underline=True)  #Styling as a link
    currentTitle.tag_bind("full_text_link", "<Button-1>", lambda e: OpenURL(story['url']))  #Binding the click event to the whole text



    ############################


    currentSummary = Text(NewsFrame, wrap='word', height=2, width=40)
    currentSummary.tag_configure('center', justify='left')
    currentSummary.insert('1.0', story['summary'], 'left')
    currentSummary.config(state='disabled')
    currentSummary.grid(row=2, column=1, columnspan=2, sticky='nsew')


    currentDate = Label(NewsFrame, text=ConvertTimestamp(story['time_published']))
    currentAuthor = Label(NewsFrame, text=str(story['authors']))
    currentAuthor.grid(row=3, column=1,columnspan=2, sticky='nsew')
    currentDate.grid(row=4, column=1,columnspan=2, sticky='nsew')
    

    forwardButton = Button(NewsFrame, text="->", command=lambda: ChangeArticleIndex(index, len(stories), 'forward', stories, NewsFrame, publicFrame))
    backButton = Button(NewsFrame, text="<-", command=lambda: ChangeArticleIndex(index, len(stories), 'back', stories, NewsFrame, publicFrame))

    
    backButton.grid(row=5, column=1, columnspan=1)
    forwardButton.grid(row=5, column=2, columnspan=1)
    


#############################CANDLE STICK CHART########################################

def ChangeChart(dateType, reportDict, CandleChartFrame):


    global canvas
    canvas.delete(all)

    canvas = FigureCanvasTkAgg(reportDict['candle'][dateType]['fig'], master=CandleChartFrame)
    canvas.draw()
    canvas = canvas.get_tk_widget()
    canvas.grid(row=0, column=0, sticky='w')


    buttonFrame = Frame(CandleChartFrame)
    buttonFrame.grid(row=1, column=0, sticky='nsew')
    buttonFrame.grid_rowconfigure(1, weight=1, uniform="equal")
    

    dateRanges = ['1D', '5D', '1M', '3M', '6M', '1Y']
    for i in range(len(dateRanges)):
        buttonFrame.grid_columnconfigure(i, weight=1, uniform="equal")
        Button(buttonFrame, text=dateRanges[i], command=lambda i=i: ChangeChart(dateRanges[i], reportDict, CandleChartFrame)).grid(row=1, column=i)

#Adds the Candle Stick chart to the screen 
def PlaceCandleChart(reportDict):

    CandleChartFrame = Frame(root, bg='white')
    CandleChartFrame.grid(row=3, column=1, sticky='nsew')

    CandleChartFrame.grid_rowconfigure(0, weight=9, uniform="equal")  #canvas
    CandleChartFrame.grid_rowconfigure(1, weight=1, uniform="equal")  #buttons
    CandleChartFrame.grid_columnconfigure(0, weight=1, uniform="equal")


    
    #Create a canvas widget to embed the Matplotlib figure into the Tkinter window
    global canvas
    canvas = FigureCanvasTkAgg(reportDict['candle']['1D']['fig'], master=CandleChartFrame)
    canvas.draw()
    canvas = canvas.get_tk_widget()
    canvas.grid(row=0, column=0, sticky='w')


    buttonFrame = Frame(CandleChartFrame)
    buttonFrame.grid(row=1, column=0, sticky='nsew')
    buttonFrame.grid_rowconfigure(1, weight=1, uniform="equal")
    
    dateRanges = ['1D', '5D', '1M', '3M', '6M', '1Y']
    for i in range(len(dateRanges)):
        buttonFrame.grid_columnconfigure(i, weight=1, uniform="equal")
        Button(buttonFrame, text=dateRanges[i], command=lambda i=i: ChangeChart(dateRanges[i], reportDict, CandleChartFrame)).grid(row=1, column=i)


##########################################################
#Get Stock Info
def LookupStock(tickerSymbol, welcomeFrame=None):

    reportDict = {
        'ticker': tickerSymbol,
        'candle': {
            }

    }

    #Candle Stick Charts
    dateTypes = ['1D', '5D', '1M', '3M', '6M', '1Y']
    for dateType in dateTypes:
        reportDict['candle'][dateType] = {}
        reportDict['candle'][dateType]['fig'], reportDict['candle'][dateType]['ax'] = GetCandleChart(tickerSymbol, dateType)

    
    #News Stories
    newsStories = GetNewsData(tickerSymbol)
    reportDict['stories'] = newsStories

    #Tweets/X
    tweets = GetTweets(tickerSymbol)
    reportDict['tweets'] = tweets


    BuildReportScreen(reportDict, welcomeFrame)


#########################################################


root.mainloop()