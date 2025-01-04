import requests
import mplfinance as mpf
import pandas as pd

def GetCandleChart(tickerSymbol, dateType):

    dateSearch = None
    searchExtension = None
    requireSlice = True

    if dateType == '1D':

        dateSearch = 'function=' + 'TIME_SERIES_INTRADAY'
        timeInterval = '&interval=' + '1min'
        searchExtension = dateSearch + timeInterval
        key = 'Time Series (1min)'
        requireSlice = False


    elif dateType == '5D':
        dateSearch = 'function=' + 'TIME_SERIES_INTRADAY'
        timeInterval = '&interval=' + '15min'
        outputsize = '&outputsize=' + 'full'
        searchExtension = dateSearch + timeInterval + outputsize
        key = 'Time Series (15min)'

        N = 5

    
    elif dateType == '1M':
        dateSearch = 'function=' + 'TIME_SERIES_INTRADAY'
        timeInterval = '&interval=' + '30min'
        outputsize = '&outputsize=' + 'full'
        searchExtension = dateSearch + timeInterval + outputsize
        key = 'Time Series (30min)'

        requireSlice = False

    elif dateType == '3M':
        dateSearch = 'function=' + 'TIME_SERIES_DAILY'
        outputsize = '&outputsize=' + 'compact'
        searchExtension = dateSearch + outputsize
        key = 'Time Series (Daily)'

        from TimeScript import daysLastMonthN
        N  = daysLastMonthN(3)

    elif dateType == '6M':
        dateSearch = 'function=' + 'TIME_SERIES_DAILY'
        outputsize = '&outputsize=' + 'full'
        searchExtension = dateSearch + outputsize
        key = 'Time Series (Daily)'

        from TimeScript import daysLastMonthN
        N  = daysLastMonthN(6)

    elif dateType == '1Y':
        dateSearch = 'function=' + 'TIME_SERIES_DAILY'
        outputsize = '&outputsize=' + 'full'
        searchExtension = dateSearch + outputsize
        key = 'Time Series (Daily)'

        from TimeScript import daysLastMonthN
        N  = daysLastMonthN(12)
        

    import secret
    url = f'https://www.alphavantage.co/query?{searchExtension}&symbol={tickerSymbol}&apikey={secret.AV_API_Key}'


    r = requests.get(url)
    data = r.json()

    sortedKeys = sorted(data.keys())
    key = sortedKeys[1]

    timeSeries = data[key]


    if requireSlice:
        #code to slice appropriately.
        from TimeScript import RecentFromDict
        newTimeSeries =  RecentFromDict(timeSeries, N)
    else:
        newTimeSeries = timeSeries


    #Preparing data for the DataFrame
    dataList = []
    for timestamp, values in newTimeSeries.items():
        dataList.append([
            timestamp, 
            float(values['1. open']), 
            float(values['2. high']), 
            float(values['3. low']), 
            float(values['4. close']),
            int(values['5. volume'])
        ])



    #Converting list to DataFrame
    df = pd.DataFrame(dataList, columns=['Date', 'Open', 'High', 'Low', 'Close', 'Volume'])

    #'Date' column to datetime format
    df['Date'] = pd.to_datetime(df['Date'])

    #Sorting Date index
    df = df.sort_values('Date', ascending=True)

    #Setting the 'Date' column as the index
    df.set_index('Date', inplace=True)





    ############
    #We calculate bounds in this next p-art so that huge high and lows don't affect the visibility of the chart
    
    #Get highest and lowest Open/Close values
    highestOpenClose = df[['Open', 'Close']].max().max()
    lowestOpenClose = df[['Open', 'Close']].min().min()

    #Calculate the total range (highest - lowest)
    totalRange = highestOpenClose - lowestOpenClose

    #80% of the canvas for lowest to highest price - 10% padding on either side
    chartExcess = totalRange*0.1

    #Calculate the zoomed range
    adjustedHigh = highestOpenClose + (chartExcess)
    adjustedLow = lowestOpenClose - (chartExcess)



    ############

    fig, ax = mpf.plot(df, 
                       type='candle', 
                       style='charles', 
                       title=f'Price Over the Span of {dateType}',
                       ylim=(adjustedLow, adjustedHigh),
                       returnfig=True,
                       tight_layout=False)

    return fig, ax


def GetNewsData(tickerSymbol):

    import secret

    url = f'https://www.alphavantage.co/query?function=NEWS_SENTIMENT&tickers={tickerSymbol}&apikey={secret.AV_API_Key}'
    r = requests.get(url)
    data = r.json()

    try:
        stories = data['feed']
    
    except:
        print('issue with alpha vantage story')

    
    return stories
