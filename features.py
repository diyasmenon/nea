# all imports
import dbUtility

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
        return []  # no sizes selected, return empty list

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
        return []

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

