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