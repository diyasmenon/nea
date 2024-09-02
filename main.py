#all imports
from flask import Flask, render_template, request, redirect, session, url_for, flash
import mysql.connector
from config import Config
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
# gets settings from Config class
app.config.from_object(Config)

# gets the db connection with useraccountsdb
def getDBConnection():
    connection = mysql.connector.connect(
        host=app.config['MYSQL_HOST'],
        user=app.config['MYSQL_USER'],
        password=app.config['MYSQL_PASSWORD'],
        database=app.config['MYSQL_DB']
    )
    return connection



@app.route('/')
def home():
    return render_template('homePage.html')



@app.route('/login', methods=["GET", "POST"])
def login():

    # var to store error messages
    pwdError = None
    emailError = None
    # the css class for the email input field
    pwdClass = ""
    emailClass = ""

    if request.method == "POST":

        #get the data in the login form and saves them in a variable
        email = request.form["email"]
        password = request.form["password"]

        #gets password for that email address from db

        db = getDBConnection()
        # returns the values as a dictionary
        cursor = db.cursor(dictionary=True)
        # selects all the data for that email address
        cursor.execute('SELECT * FROM userAccountsTBL WHERE email=%s', (email,))
        # only need to get corresponding user info
        user = cursor.fetchone()
        # closes all the connetions
        cursor.close()
        db.close()

        # checking if user exists and hashed pwds match
        if user and check_password_hash(user['password'], password):
            # stores info about user for their session
            session['user_id'] = user['id']

            return redirect(url_for('home'))
        
        # if user doesn't exist
        elif not user:
            # gives error message and css class to highlight input box
            emailError = "This email does not have an account"
            # adds an error class to the input field
            emailClass = "error"

        # if pwd don't match
        else:
            # gives error message and css class to highlight input box
            pwdError = "Incorrect password"
            # adds an error class to the input field
            pwdClass = "error"
    
    return render_template('loginPage.html', emailError=emailError, pwdError=pwdError, emailClass=emailClass, pwdClass=pwdClass)



@app.route('/signup', methods=["GET", "POST"])
def signup():

    # var to store error messages
    emailError = None
    # the css class for the email input field
    emailClass = ""

    if request.method == "POST":

        #get the data in the sign up form and saves them in a variable
        firstName = request.form["firstName"]
        email = request.form["email"]
        password = request.form["password"]

        # creates a hashed version of the password
        hashedPassword = generate_password_hash(password)

        #store the data in useraccountsdb

        db = getDBConnection()
        cursor = db.cursor()

        # checks if email already registered
        cursor.execute('SELECT * FROM userAccountsTBL WHERE email = %s', (email,))
        # only need to get one user
        user = cursor.fetchone()

        # sees if a user exists
        if user:
            # gives error message and css class to highlight input box
            emailError = "Email already in use"
            # adds an error class to the input field
            emailClass = "error"
            cursor.close()
            db.close()
        else:
            # inserts data into db
            cursor.execute('INSERT INTO userAccountsTBL (email, password, firstName) VALUES (%s, %s, %s)', (email, hashedPassword, firstName))
            # commits the values in db
            db.commit()
            # closes all the connetions
            cursor.close()
            db.close()
        
            # takes them to the home page
            return redirect(url_for('home'))

    return render_template('signupPage.html', emailError=emailError, emailClass=emailClass)



if __name__ == '__main__':
    app.run(debug=True)