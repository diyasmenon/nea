import mysql.connector
from config import Config # gets the config info from external file


# gets the db connection with useraccountsdb
def getDBConnection():
    connection = mysql.connector.connect(
        host=Config.MYSQL_HOST,
        user=Config.MYSQL_USER,
        password=Config.MYSQL_PASSWORD,
        database=Config.MYSQL_DB
    )
    return connection