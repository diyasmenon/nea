# all imports
import requests
from apscheduler.schedulers.background import BackgroundScheduler
import dbUtility


# gets the data from the rasb pi
def fetchData():
    try:
        rasbPiIP = "http://192.168.68.125:5000/sensorData"
        sensorData = requests.get(rasbPiIP)

        if sensorData.status_code == 200: # if data has been collected
            data = sensorData.json()  # get the data from the response

            # store this data in the db
            db = dbUtility.getDBConnection()
            cursor = db.cursor()

            # adds each concentration for each sized particle
            # inserts data into db for each
            query = 'INSERT INTO particleDataTbl (apiKey, timestamp, concentration, particleCategory) VALUES (%s, %s, %s, %s)'
            cursor.execute(query, (data['apiKey'], data['time'], data['PM1.0'], 'PM1.0'))
            cursor.execute(query, (data['apiKey'], data['time'], data['PM2.5'], 'PM2.5'))
            cursor.execute(query, (data['apiKey'], data['time'], data['PM10.0'], 'PM10.0'))

            # inserts the actual value into the prediction table, to be able to compare them
            query = 'UPDATE predictionTbl SET actualValue = %s WHERE timestamp = %s AND particleCategory = %s AND apiKey = %s'
            cursor.execute(query, (data['PM1.0'], data['time'], 'PM1.0', data['apiKey'] ))
            cursor.execute(query, (data['PM2.5'], data['time'], 'PM2.5', data['apiKey']))
            cursor.execute(query, (data['PM10.0'], data['time'], 'PM10.0', data['apiKey']))

            # commits the values in db
            db.commit()
            # closes all the connetions
            cursor.close()
            db.close()

        else:
            print("Failed to fetch data.")

    except requests.exceptions.RequestException as error:
        print(f"Error fetching data: {error}")

# deletes particle data, when it has expired (wont be needed and saves space)
def deleteOldData():
    db = dbUtility.getDBConnection()
    cursor = db.cursor()
    # deleted particle readings older than 1 hour
    cursor.execute('DELETE FROM particleDataTbl WHERE timestamp < NOW() - INTERVAL 1 HOUR;')
    # deletes the prediction data older than a minute
    cursor.execute('DELETE FROM predictionTbl WHERE timestamp < NOW() - INTERVAL 1 MINUTE;')
    # commits the values in db
    db.commit()
    # closes all the connetions
    cursor.close()
    db.close()


# schedulers to run tasks periodically
scheduler = BackgroundScheduler()
# runs fetchData() every 1 second
scheduler.add_job(fetchData, 'interval', seconds=1)
# runs deleteOldData() every 2 minutes
scheduler.add_job(deleteOldData, 'interval', minutes=2)
scheduler.start()