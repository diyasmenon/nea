# all imports
import requests
from apscheduler.schedulers.background import BackgroundScheduler
import dbUtility


# gets the data from the rasb pi
def fetchData():
    try:
        rasbPiIP = "http://192.168.68.107:5000/sensorData"
        sensorData = requests.get(rasbPiIP)

        if sensorData.status_code == 200: # if data has been collected
            data = sensorData.json()  # get the data from the response

            # store this data in the db
            db = dbUtility.getDBConnection()
            cursor = db.cursor()

            # adds each concentration for each sized particle
            # inserts data into db for each
            cursor.execute('INSERT INTO particleDataTbl (apiKey, time, concentration, particleCategory) VALUES (%s, %s, %s, %s)', (data['apiKey'], data['time'], data['PM1.0'], 'PM1.0'))
            cursor.execute('INSERT INTO particleDataTbl (apiKey, time, concentration, particleCategory) VALUES (%s, %s, %s, %s)', (data['apiKey'], data['time'], data['PM2.5'], 'PM2.5'))
            cursor.execute('INSERT INTO particleDataTbl (apiKey, time, concentration, particleCategory) VALUES (%s, %s, %s, %s)', (data['apiKey'], data['time'], data['PM10.0'], 'PM10.0'))
            
            # commits the values in db
            db.commit()
            # closes all the connetions
            cursor.close()
            db.close()
        else:
            print("Failed to fetch data.")

    except requests.exceptions.RequestException as error:
        print(f"Error fetching data: {error}")



# deletes particle data, when it has been over an hour (wont be needed and saves space)
def deleteOldData():
    db = dbUtility.getDBConnection()
    cursor = db.cursor()
    cursor.execute('DELETE FROM particleDataTbl WHERE time < NOW() - INTERVAL 1 HOUR;')
    # commits the values in db
    db.commit()
    # closes all the connetions
    cursor.close()
    db.close()

# schedulers to run tasks periodically
scheduler = BackgroundScheduler()
# runs fetchData() every 5 seconds
scheduler.add_job(fetchData, 'interval', seconds=5)
# runs deleteOldData() every 2 minutes
scheduler.add_job(deleteOldData, 'interval', minutes=2)
scheduler.start()