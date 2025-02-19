# all imports
import dbUtility # to use the db
from datetime import datetime # to get current time

def getCurrentTime(apiKey):
    db = dbUtility.getDBConnection()
    cursor = db.cursor()
    cursor.execute('SELECT MAX(time) FROM particleDataTbl WHERE apiKey = %s', (apiKey,))
    # stores the time
    time = cursor.fetchone()[0]
    # closes all the connetions
    cursor.close()
    db.close()

    return time

def getCurrentConcs(apiKey):
    db = dbUtility.getDBConnection()
    cursor = db.cursor()

    # gets the latest reading for each category
    # pm 1.0
    cursor.execute(
        '''
        SELECT concentration
        FROM particleDataTbl 
        WHERE apiKey = %s 
        AND particleCategory = 'PM1.0'
        ORDER BY time DESC
        LIMIT 1
        ''', (apiKey,))
    
    # stores the data of pm1.0
    pm1_0 = cursor.fetchall()[0] # gives conc for pm1.0

    # pm 2.5
    cursor.execute(
        '''
        SELECT concentration
        FROM particleDataTbl 
        WHERE apiKey = %s 
        AND particleCategory = 'PM2.5'
        ORDER BY time DESC
        LIMIT 1
        ''', (apiKey,))
    
    # stores the data of pm2.5
    pm2_5 = cursor.fetchall()[0] # gives conc for pm2.5

    # pm 10.0
    cursor.execute(
        '''
        SELECT concentration
        FROM particleDataTbl 
        WHERE apiKey = %s 
        AND particleCategory = 'PM10.0'
        ORDER BY time DESC
        LIMIT 1
        ''', (apiKey,))
    
    # stores the data of pm10.0
    pm10_0 = cursor.fetchall()[0] # gives conc for pm10.0

    data = {
        'PM1.0': pm1_0[0],
        'PM2.5': pm2_5[0],
        'PM10.0': pm10_0[0]
    }

    # closes all the connetions
    cursor.close()
    db.close()

    return data

# gets the relevent data for the selected time frame and sizes
def getConcData(timeframe, pm1_0, pm2_5, pm10_0):

    sizes = []

    # adds all relevant sizes selected
    if pm1_0:
        sizes.append('PM1.0')
    if pm2_5:
        sizes.append('PM2.5')
    if pm10_0:
        sizes.append('PM10.0')

    if not sizes:
        return {}  # no sizes selected, return empty dict

    db = dbUtility.getDBConnection()
    cursor = db.cursor()

    # if only one size selected, dont need to pass it in as a tuple 
    # ensures code doesnt break and works as intended
    if len(sizes) == 1:
        # get relevant data dependent on parameters
        query =f'''
            SELECT time, concentration, particleCategory
            FROM particleDataTbl 
            WHERE time >= NOW() - INTERVAL {timeframe}
            AND particleCategory = '{sizes[0]}'
            ORDER BY time ASC
            '''

    else:
        # get relevant data dependent on parameters
        query =f'''
            SELECT time, concentration, particleCategory
            FROM particleDataTbl 
            WHERE time >= NOW() - INTERVAL {timeframe}
            AND particleCategory IN {tuple(sizes)}
            ORDER BY time ASC   
            '''

    try:
        # execute the query with parameters
        cursor.execute(query)  # pass timeframe and sizes
    except Exception as e:
        print(f"Error executing query: {e}")
        return {}

    # stores the data (as a tuple)
    data = cursor.fetchall()

    # closes all the connetions
    cursor.close()
    db.close()

    # initialise output dictionary
    formattedData = {"time": [], "PM1.0": [], "PM2.5": [], "PM10.0": []}

    # process data into the right format
    for row in data:
        
        # convert datetime to string
        timeString = row[0].strftime("%Y-%m-%d %H:%M:%S") 

        if row[0].strftime("%Y-%m-%d %H:%M:%S") not in formattedData["time"]:
            formattedData["time"].append(timeString)
            # adding placeholder values for concentrations so that they don't get unaligned
            formattedData["PM1.0"].append(None)
            formattedData["PM2.5"].append(None) 
            formattedData["PM10.0"].append(None) 
        
        # get index of the timestamp
        index = formattedData["time"].index(timeString)
    
        if row[2] == "PM1.0":
            formattedData["PM1.0"][index] = row[1]
        elif row[2] == "PM2.5":
            formattedData["PM2.5"][index] = row[1]
        elif row[2] == "PM10.0":
            formattedData["PM10.0"][index] = row[1]

    return formattedData

def getHistoricalTrendsData(data):
    # if multiple sizes are chosen, the smallest is taken into consideration
    
    # choosing which size to focus on, as long as they have non-None values
    #   in the data set
    if data and len(data['time']) > 1:
        if not all(conc is None for conc in data['PM1.0']):
            size = 'PM1.0'
        elif not all(conc is None for conc in data['PM2.5']):
            size = 'PM2.5'
        elif not all(conc is None for conc in data['PM10.0']):
            size = 'PM10.0'
    else:
        # runs if no size is selected
        # default value of 'N/A' is displayed
        size = 'N/A'
        overallTrend = 'N/A'
        peakInfo = 'N/A' 
        avgConc = 'N/A'

        # returns all these values to display
        return size, overallTrend, peakInfo, avgConc

    # gets the relevent data for the size as an array from the dictionary
    conc = data[size]

    # work out the overall trend using the gradient

    num = len(conc)
    x = list(range(num)) # assume the readings taken at equal intervals
    y = conc

    # finding out the mean for each value
    meanX = sum(x) / num
    meanY = sum(y) / num

    # calculate the covariance between time and conc
    # measures how much each varies
    numerator = sum((x[i] - meanX) * (y[i] - meanY) for i in range(num))
    # calculate the variance of time and prevents 0 division
    denominator = sum((x[i] - meanX) ** 2 for i in range(num))

    # calulate the gradient
    gradient = numerator/denominator

    # threshold to allow roughly stable data to exist
    THRESHOLD = 0.001

    # converting gradient to a trend value
    if gradient > THRESHOLD:
        overallTrend = 'Increasing'
    elif gradient < -THRESHOLD:
        overallTrend = 'Decreasing'
    else:
        overallTrend = 'Stable'

    #print(gradient, overallTrend)

    # work out the maximum conc and what time

    # get the right peak value and time it occurs at
    peak = max(conc)
    index = conc.index(peak)
    # get the peak time in the right format
    peakTime = datetime.strptime(data['time'][index], "%Y-%m-%d %H:%M:%S")

    # get the current time
    currentTime = datetime.now()
    # calculate time difference
    timeDiff = abs(currentTime - peakTime)

    # extract hours, minutes, and seconds
    hours, remainder = divmod(timeDiff.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)

    # puts the time diff in the correct format to display
    if hours:
        # maximum time diff is 1h
        peakInfo = f'{peak} µg/m³ (1h ago)'
    elif minutes:
        peakInfo = f'{peak} µg/m³ ({minutes}m {seconds}s ago)'
    elif seconds:
        peakInfo = f'{peak}µg/m³ ({seconds}s ago)'
    else:
        peakInfo = f'{peak} µg/m³ (now)'

    # works out the average conc for this size particle
    # rounds the value to 2 dp
    avgConc = round((sum(conc)/len(conc)), 2)
    # formats it nicely
    avgConc = f'{avgConc} µg/m³'

    # return all relevent data to display
    return size, overallTrend, peakInfo, avgConc