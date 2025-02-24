# all imports
from flask import Flask, render_template, request, redirect, session, url_for, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import secrets # for generating an api for the user
import json # for formatting the data correctly

# custom modules
from config import Config
import dbUtility
import dataHandler
import features


app = Flask(__name__)
# gets settings from Config class
app.config.from_object(Config)


# ALL WEBPAGE ROUTES


@app.route('/')
def home():
    if 'apiKey' in session:
        loggedIn = True

    else:
        loggedIn = False

    return render_template('homePage.html', loggedIn = loggedIn)



@app.route('/login', methods=["GET", "POST"])
def login():

    # var to store error messages
    pwdError = None
    emailError = None
    # the css class for the email input field
    pwdClass = ""
    emailClass = ""

    if request.method == "POST":

        # get the data in the login form and saves them in a variable
        email = request.form["email"]
        password = request.form["password"]

        # gets password for that email address from db

        db = dbUtility.getDBConnection()
        # returns the values as a dictionary
        cursor = db.cursor(dictionary=True)
        # selects all the data for that email address
        cursor.execute('SELECT * FROM userAccountsTbl WHERE email=%s', (email,))
        # only need to get corresponding user info
        user = cursor.fetchone()
        # closes all the connections
        cursor.close()
        db.close()

        # checking if user exists and hashed pwds match
        if user and check_password_hash(user['password'], password):
            # stores info about user for their session
            session['apiKey'] = user['apiKey']

            #redirects the user to the dashboard when logged in
            return redirect(url_for('dashboard'))
        
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

        # create a 64-char unique api key with the library secrets
        apiKey = secrets.token_hex(32)


        #store the data in useraccountsdb

        db = dbUtility.getDBConnection()
        cursor = db.cursor()

        # checks if email already registered
        cursor.execute('SELECT * FROM userAccountsTbl WHERE email = %s', (email,))
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
            query = 'INSERT INTO userAccountsTbl (apiKey, email, password, firstName) VALUES (%s, %s, %s, %s)'
            cursor.execute(query, (apiKey, email, hashedPassword, firstName))
            # commits the values in db
            db.commit()
            # closes all the connetions
            cursor.close()
            db.close()
        
            # starts their session
            session['apiKey'] = apiKey

            # takes them to the dashboard when created
            return redirect(url_for('dashboard'))

    return render_template('signupPage.html', emailError=emailError, emailClass=emailClass)



@app.route('/logout')
def logout():

    #removes user_id from session
    session.pop('apiKey', None)
    return redirect(url_for('login'))  # redirect to login



@app.route('/dashboard')
def dashboard():

    # checks if the user is logged in and gives appropriate boolean response
    # determines if a user can access this page yet
    if 'apiKey' in session:
        loggedIn = True

    else:
        loggedIn = False

    return render_template('dashboardPage.html', loggedIn = loggedIn, apiKey = session['apiKey'])



@app.route('/analytics')
def analytics():

    # checks if the user is logged in and gives appropriate boolean response
    # determines if a user can access this page yet
    if 'user_id' in session:
        loggedIn = True

    else:
        loggedIn = False

    return render_template('dataAnalyticsPage.html', loggedIn = loggedIn)


# ALL DASHBOARD/ANALYTICS FEATURES ROUTES


@app.route('/currentTimeFeature') # for both pages
def currentTimeFeature():
    # gets the latest time stored in db belonging to the specific user
    time = features.getCurrentTime(session['apiKey'])
    # returns this as a dictionary
    return jsonify({'time':time})

@app.route('/currentConcsFeature') # only for dashboard
def currentConcsFeature():
    # gets the latest particle concs stored in db belonging to the specific user
    data = features.getCurrentConcs(session['apiKey'])
    # returns the data
    return jsonify(data)

@app.route('/concGraphFeature') # only for dashboard
def concGraphFeature():
    # gets data for all particle sizes from the last 10 minutes
    # apiKey used to retrieve
    data = features.getConcData('10 MINUTE', True, True, True, session['apiKey'])
    return jsonify(data)

@app.route('/analyticsFeatures', methods=['POST']) # only for analytics
def analyticsFeatures():
    # gets data for relevant particle sizes for the given timeframe
    # all depends on what the user chooses on the website

    # get data from request
    data = request.json
    timeframe = data.get("timeframe")
    pm1_0 = data.get("pm1_0")
    pm2_5 = data.get("pm2_5")
    pm10_0 = data.get("pm10_0")

    # get graph data
    data = features.getConcData(timeframe, pm1_0, pm2_5, pm10_0, session['apiKey'])

    # get historical trends using this data, to display
    historicalData = features.getHistoricalTrendsData(data)

    # get the latest data from the last 10 mins for prediction
    data = features.getConcData('10 MINUTE', pm1_0, pm2_5, pm10_0, session['apiKey'])

    # get predictive trends using this data, to display
    predictedData = features.getPredictedTrendsData(data, session['apiKey'])

    # joins the dictionaries together
    allData = {**historicalData, **predictedData}

    return jsonify(allData)


if __name__ == '__main__':
    app.run(debug=True)