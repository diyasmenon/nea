# all imports
import dbUtility # to use the db
from datetime import datetime, timedelta # to get current time

def getCurrentTime(apiKey):
    db = dbUtility.getDBConnection()
    cursor = db.cursor()
    cursor.execute('SELECT MAX(timestamp) FROM particleDataTbl WHERE apiKey = %s', (apiKey,))
    # stores the time
    time = cursor.fetchone()[0]

    # runs if time is None

    if not time:
        time = 'Hardware Failed'

    # closes all the connetions
    cursor.close()
    db.close()

    return time

def getCurrentConcs(apiKey):
    db = dbUtility.getDBConnection()
    cursor = db.cursor()

    # gets the latest reading for each category

    query = '''
        SELECT concentration
        FROM particleDataTbl 
        WHERE apiKey = %s 
        AND particleCategory = %s
        ORDER BY timestamp DESC
        LIMIT 1
        '''
    
    # pm 1.0
    cursor.execute(query, (apiKey, 'PM1.0'))
    # stores the data of pm1.0
    pm1_0 = cursor.fetchall()# gives conc for pm1.0

    # pm 2.5
    cursor.execute(query, (apiKey, 'PM2.5'))
    # stores the data of pm2.5
    pm2_5 = cursor.fetchall() # gives conc for pm2.5

    # pm 10.0
    cursor.execute(query, (apiKey, 'PM10.0'))
    # stores the data of pm10.0
    pm10_0 = cursor.fetchall() # gives conc for pm10.0

    try:
        data = {
            'PM1.0': pm1_0[0][0],
            'PM2.5': pm2_5[0][0],
            'PM10.0': pm10_0[0][0]
        }
    except:
        # runs if concentrations do not exist for the user at all
        # gives appropriate error message
        data = {
            'PM1.0': 'Hardware Failed',
            'PM2.5': 'Hardware Failed',
            'PM10.0': 'Hardware Failed'
        }

    # closes all the connetions
    cursor.close()
    db.close()

    return data

def getConcData(timeframe, pm1_0, pm2_5, pm10_0, apiKey):
    # gets the relevent data for the selected time frame and sizes

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
            SELECT timestamp, concentration, particleCategory
            FROM particleDataTbl 
            WHERE timestamp >= NOW() - INTERVAL {timeframe}
            AND particleCategory = '{sizes[0]}'
            AND apiKey = '{apiKey}'
            ORDER BY timestamp ASC
            '''

    else:
        # get relevant data dependent on parameters
        query =f'''
            SELECT timestamp, concentration, particleCategory
            FROM particleDataTbl 
            WHERE timestamp >= NOW() - INTERVAL {timeframe}
            AND particleCategory IN {tuple(sizes)}
            AND apiKey = '{apiKey}'
            ORDER BY timestamp ASC   
            '''

    try:
        # execute the query with parameters
        cursor.execute(query)  # pass timeframe and sizes
    except Exception as e:
        # if no valid readings for the user
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
        data['size'] = 'N/A'
        data['overallTrend'] = 'N/A'
        data['peakInfo'] = 'N/A'
        data['avgConc'] = 'N/A'

        # returns all these values to display
        return data

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

    # add these values to the big data dictionary
    data['size'] = size
    data['overallTrend'] = overallTrend
    data['peakInfo'] = peakInfo
    data['avgConc'] = avgConc

    # return all relevent data to display
    return data

def getPredictedTrendsData(data, apiKey):

    # predicting the next 20 values for all data sizes chosen

    # initialising the variables
    predictedPM1_0 = []
    predictedPM2_5 = []
    predictedPM10_0 = []

    # need atleast 4 previous values to calculate future ones
    # condition checks if each value isnt equal to None and adds 
    #   one to a list and sums it
    if data: #checks if there is data [ie any size selected]
        if sum(1 for conc in data['PM1.0'] if conc is not None) > 3:
            # if theres enough data, call the function to predict the data depending on the
            #   datset given
            predictedPM1_0 = predictNextValues(data['PM1.0'])
        if sum(1 for conc in data['PM2.5'] if conc is not None) > 3:
            predictedPM2_5 = predictNextValues(data['PM2.5'])
        if sum(1 for conc in data['PM10.0'] if conc is not None) > 3:
            predictedPM10_0 = predictNextValues(data['PM10.0'])

    else:
        # gives placeholder values
        predictedData = {}
        predictedData['Analytics PM1.0'] = []
        predictedData['Analytics PM2.5'] = []
        predictedData['Analytics PM10.0'] = []
        predictedData['Analytics Times'] = []
        predictedData['Predicted Times'] = []
        predictedData['Predicted PM1.0'] = []
        predictedData['Predicted PM2.5'] = []
        predictedData['Predicted PM10.0'] = []

        return predictedData

    time = data['time']

    # saves this data as a dictionary
    predictedData = {}

    # adds placeholders for the graph depending on amount of predicted data
    # placeholders are after the actual values in the list
    predictedData['Analytics PM1.0'] = data['PM1.0'] + ([None] * len(predictedPM1_0))
    predictedData['Analytics PM2.5'] = data['PM2.5'] + ([None] * len(predictedPM2_5))
    predictedData['Analytics PM10.0'] = data['PM10.0'] + ([None] * len(predictedPM10_0))
    predictedData['Analytics Times'] = time

    #  n is the number of predictions, we need to find it as some lengths of predictions would
    #   be 0 as that size wasnt selected. this finds the largest n value

    n = len(predictedPM1_0)
    if len(predictedPM2_5) > n:
        n = len(predictedPM2_5)
    if len(predictedPM10_0) > n:
        n = len(predictedPM10_0)

    # giving placeholder values for time to show it isnt recorded data
    predictedData['Predicted Times'] = ['.'] * n
    # adding placeholders before the actual predictions
    predictedData['Predicted PM1.0'] = ([None] * len(data['PM1.0'])) + predictedPM1_0
    predictedData['Predicted PM2.5'] = ([None] * len(data['PM2.5'])) + predictedPM2_5
    predictedData['Predicted PM10.0'] = ([None] * len(data['PM10.0'])) + predictedPM10_0

    # store the prediction in a db to help calculate its accurary
    #   passes through the relevant size of particle
    storePrediction(predictedPM1_0, 'PM1.0', apiKey)
    storePrediction(predictedPM2_5, 'PM2.5', apiKey)
    storePrediction(predictedPM10_0, 'PM10.0', apiKey)

    # SUMMARY DATA

    # finds the smallest value selected
    # one has to be selected else it wouldve been caught at the beginning of function
    if not all(conc is None for conc in data['PM1.0']):
        size = 'PM1.0'
    elif not all(conc is None for conc in data['PM2.5']):
        size = 'PM2.5'
    elif not all(conc is None for conc in data['PM10.0']):
        size = 'PM10.0'

    # get the relevant data for the past 1 min
    db = dbUtility.getDBConnection()
    cursor = db.cursor()
    query = f'''
        SELECT predictedValue, actualValue 
        FROM predictionTbl 
        WHERE timestamp >= NOW() - INTERVAL 1 MINUTE
        AND apiKey = '{apiKey}'
    '''
    cursor.execute(query)
    # stores the data
    confidenceData = cursor.fetchall()
    # closes all the connetions
    cursor.close()
    db.close()

    # clean the data
    cleanedConfidenceData = []

    # repeats for each pair of values (predicted and actual data)
    for reading in confidenceData:
        # if the actual data does exist for the predicted (ie reading was taken at the predicted time)
        if reading[1] != None:
            # add the pair of data into a list to manipulate
            cleanedConfidenceData.append(reading)

    # avoid 0 division
    if len(cleanedConfidenceData) > 0:
        totalError = 0 # a var to count the total error between actual and predicted
        errorList = [] # makes a list of the error values
        for reading in cleanedConfidenceData:
            # gives the absolute difference between the values
            error = abs(reading[0] - reading[1])
            # adds this error to the total
            totalError += error
            # adds this error to the error list for later
            errorList.append(error)

        # confidence level

        # works out the avg error across all data points
        avgError = totalError / len(cleanedConfidenceData)

        # find the mean between all actual values
        avgActual = sum(reading[1] for reading in cleanedConfidenceData) / len(cleanedConfidenceData)

        # caclulates confidence with a formula to 1 dp
        confidence = round(((1 - (avgError/avgActual)) * 100), 1)

        # uncertainty

        # work out the variance of the errors
        variance = sum((e - avgError) ** 2 for e in errorList) / len(cleanedConfidenceData)
        standardDeviation = variance ** 0.5  # work out standard deviation
        # uncertainty is set as ± one standard deviation (rounded)
        uncertainty = round(standardDeviation, 2)

        # recent prediction deviation
    
        N = 5  # number of recent readings to consider (may need to adjust)
        
        if len(cleanedConfidenceData) >= N:
            # subset of confidenceData
            recentData = cleanedConfidenceData[-N:]  # take the last N readings

            # work out absolute deviations
            recentDeviations = [abs(reading[0] - reading[1]) for reading in recentData]

            # find average deviation
            avgRecentDeviation = sum(recentDeviations) / len(recentDeviations)

            # work out mean actual value for recent data
            avgActualRecent = sum(reading[1] for reading in recentData) / len(recentData)

            # work out percentage deviation
            percentRecentDeviation = (avgRecentDeviation / avgActualRecent) * 100

            # round results so its in the right format
            avgRecentDeviation = round(avgRecentDeviation, 2)
            percentRecentDeviation = round(percentRecentDeviation, 1)
            predictionDeviation = f'± {avgRecentDeviation}µg/m³ ({percentRecentDeviation}%)'
    else:
        # if theres not any data points, confidence is N/A
        confidence = 'N/A'
        uncertainty ='N/A'
        predictionDeviation = 'N/A'

    predictedData['Confidence'] = f'{confidence}%'
    predictedData['Uncertainty'] = f'±{uncertainty} µg/m³'
    predictedData['Prediction Deviation'] = predictionDeviation

    # return all the data (actual time and concs + predicted times and concs)
    # format is all good to directly plot on a graph and give the illusion of continuity
    return predictedData

def predictNextValues(data):
    # code to predict the next 20 values using current data given

    # works out the last three gradients
    # this helps to reduce the impact of noise
    gradient1 = (data[-1] - data[-2]) / 2
    gradient2 = (data[-2] - data[-3]) / 2
    gradient3 = (data[-3] - data[-4]) / 2

    # works out the average gradient
    avgGradient = (gradient1 + gradient2 + gradient3) / 3

    # stores the last point in a var for readability
    lastPoint = data[-1]

    # initialises a var to store the predicted values
    predictedValues = []

    # repeats the prediction process 20 times
    for i in range(20):
        # uses moving averages to help predict
        # adds a damping factor so it slows down
        nextValue = lastPoint + (avgGradient * (i*0.9))
        # rounds the value to 1 dp and adds it to the list
        predictedValues.append(round(nextValue, 1))

    # setting an index to get the latest reading from the past minute
    if len(data) > 59:
        index = 59
    else:
        index = len(data)

    # setting a cap for the values from a subset of data from last min
    maxValue = max(data[-index:])
    minValue = min(data[-index:])
    # reduce by 10% of range
    rangeReduction = (maxValue - minValue) * 0.1 
    adjustedMax = maxValue - rangeReduction
    adjustedMin = minValue + rangeReduction

    # if a predicted point is out of allowed range, then change them
    for i in range(len(predictedValues)):
        # gets the corresponding conc for this index
        conc = predictedValues[i]
        # checks if conc isnt in the suggested bounds and adjusts accordingly
        if conc > adjustedMax:
            predictedValues[i] = adjustedMax

        if conc < adjustedMin:
            predictedValues[i] = adjustedMin
    
    # returns the values as a list which can later be stored in a dictionary
    return predictedValues

def storePrediction(data, size, apiKey):

    # if there's no data, then there's nothing to store
    if not data:
        return
    
    # next prediction to store - only the next value
    nextPrediction = data[0]
    now = datetime.now()  # get current time
    nextSecond = now + timedelta(seconds=1)  # add 1 second

    # stores these values in a db
    db = dbUtility.getDBConnection()
    cursor = db.cursor()
    # store the prediction and the time it's thought to be at
    query = 'INSERT INTO predictionTbl (apiKey, timestamp, predictedValue, particleCategory) VALUES (%s, %s, %s, %s)'
    cursor.execute(query, (apiKey, nextSecond, nextPrediction, size))
    db.commit()  # Make sure to commit the transaction

    # closes all the connetions
    cursor.close()
    db.close()