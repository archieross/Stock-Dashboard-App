from datetime import datetime

def ConvertTimestamp(timestamp):
    print(timestamp)

    try:
        #First we try parsing as ISO 8601 with timezone
        try:
            dt = datetime.fromisoformat(timestamp)
        except ValueError:
            #If that fails, fall back to custom format (YYYYMMDDTHHMMSS) - This is for our alpha vantage API
            dt = datetime.strptime(timestamp, "%Y%m%dT%H%M%S")
        
        #Formatting the datetime object
        formatted = dt.strftime("%d %b, %Y. At %H:%M:%S UTC")
        return formatted
    except ValueError:
        return "Invalid timestamp format. Please use a valid ISO 8601 or custom format (YYYYMMDDTHHMMSS)."


def RecentFromDict(myDictionary, N):

    #Here we remove the time portion and keep a tupple of the key and value pair of original array so we can convert back after.
    #This way we can count each day individually.
    normalizedData = {}
    for k, v in myDictionary.items():
        dateOnly = datetime.strptime(k.split()[0], "%Y-%m-%d")
        if dateOnly not in normalizedData:
            normalizedData[dateOnly] = []
        normalizedData[dateOnly].append((k, v))

    #Sort all the dates in case dictionary gets them out of order.
    sortedDays = sorted(normalizedData.keys(), reverse=True)

    #Here we slice and convert back to original form.
    recentData = {}
    for day in sortedDays[:N]:
        for originalKey, value in normalizedData[day]:
            recentData[originalKey] = value

    return recentData



from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

def daysLastMonthN(N):
    currentDate = datetime.now()
    #Start at the first day of the month N months ago
    startDate = (currentDate - relativedelta(months=N)).replace(day=1)
    totalDays = 0

    for i in range(N):
        monthStart = startDate + relativedelta(months=i)
        nextMonthStart = monthStart + relativedelta(months=1)
        currentDay = monthStart

        while currentDay < nextMonthStart:
            #Check if the current day is a weekday (Monday=0, ..., Sunday=6)
            if currentDay.weekday() < 5:  #Monday to Friday
                totalDays += 1
            currentDay += timedelta(days=1)

    return totalDays

