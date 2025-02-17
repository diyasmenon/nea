# all imports
from flask import Flask, render_template, request, redirect, session, url_for
import features # imports custom modules from external file
from werkzeug.security import generate_password_hash, check_password_hash
import secrets # for generating an api for the user

# custom modules
from config import Config
import dbUtility
import dataHandler


app = Flask(__name__)
# gets settings from Config class
app.config.from_object(Config)



@app.route('/')
def home():
    if 'user_id' in session:
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
            session['user_id'] = user['id']

            return redirect(url_for('home')) #redirects the user to the home page when logged in
        
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
            cursor.execute('INSERT INTO userAccountsTbl (email, password, firstName, apiKey) VALUES (%s, %s, %s, %s)', (email, hashedPassword, firstName, apiKey))
            # commits the values in db
            db.commit()
            # closes all the connetions
            cursor.close()
            db.close()
        
            # takes them to the home page
            return redirect(url_for('home'))

    return render_template('signupPage.html', emailError=emailError, emailClass=emailClass)



@app.route('/logout')
def logout():

    #removes user_id from session
    session.pop('user_id', None)
    return redirect(url_for('home'))  # redirect to the home page



@app.route('/dashboard')
def dashboard():

    # checks if the user is logged in and gives appropriate boolean response
    # determines if a user can access this page yet
    if 'user_id' in session:
        loggedIn = True

    else:
        loggedIn = False

    # gets the users ip key to display

    userId = session.get('user_id')
    
    #connects to db
    db = dbUtility.getDBConnection()
    # returns the values as a dictionary
    cursor = db.cursor(dictionary=True)
    # selects all the data for that email address
    cursor.execute('SELECT apiKey FROM userAccountsTbl WHERE id=%s', (userId,))
    # only need to get corresponding user info
    user = cursor.fetchone()

    # if the user doesnt exist

    if not user:
        return redirect(url_for('home'))

    # gets corresponding api key
    apiKey = user['apiKey']

    # closes all the connections
    cursor.close()
    db.close()

    return render_template('dashboardPage.html', loggedIn = loggedIn, apiKey = apiKey)



@app.route('/analytics')
def analytics():

    # checks if the user is logged in and gives appropriate boolean response
    # determines if a user can access this page yet
    if 'user_id' in session:
        loggedIn = True

    else:
        loggedIn = False

    return render_template('dataAnalyticsPage.html', loggedIn = loggedIn)

if __name__ == '__main__':
    app.run(debug=True)