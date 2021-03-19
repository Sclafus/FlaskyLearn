from flask import Flask, redirect, url_for, render_template, request, session, flash
from werkzeug.utils import secure_filename
from datetime import timedelta
from Crypto.Hash import SHA256
from dotenv import load_dotenv
import mariadb
import os
import re

# loading .env file
load_dotenv()
secretKey = os.getenv("SECRET_KEY")


# .env allocation
dbUser = os.getenv("DB_USER")
dbPassword = os.getenv("DB_PASSWORD")
dbHost = os.getenv("DB_HOST")
dbPort = int(os.getenv("DB_PORT"))
dbSchema = os.getenv("DB_SCHEMA")
uploadFolder = os.getenv("UPLOAD_FOLDER")
videoFormats = os.getenv("VIDEO_FORMATS").split(', ')

# Flask inizialization
app = Flask(__name__)
app.secret_key = SHA256.new(secretKey.encode()).hexdigest()
print(f"APP SECRET KEY {app.secret_key} - {len(app.secret_key)}")
app.config['UPLOAD_FOLDER'] = uploadFolder

def doubleHash(input: str) -> str:
    '''
    return the double hash of the input string
    '''
    return SHA256.new((SHA256.new(input.encode()).hexdigest()).encode()).hexdigest()

def dbConnect():
    '''
    Returns connection to the local database object
    '''
    try:
        conn = mariadb.connect(
            user=dbUser,
            password=dbPassword,
            host=dbHost,
            port=dbPort,
            database=dbSchema
        )
        return conn

    except mariadb.Error as e:
        print(f"Error connecting to MariaDB Platform: {e}")
        raise Exception
    return None


def allowedFile(filename: str) -> bool:
    '''
    Checks if the file is currently being accepted to upload
    '''
    ext = filename.split(".")[-1]
    if ext in videoFormats:
        return True
    return False


@app.route("/")
def home():
    '''
    Renders the homepage template
    '''
    return render_template("index.html")


@app.route("/login/", methods=["POST", "GET"])
def login():
    '''
    Redirects to login.html 
    Handles POST requests to login users
    '''
    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        # handling unchecked "Remember me" option
        try:
            stayLogged = request.form["stayLogged"]
            if stayLogged:
                app.permanent_session_lifetime = timedelta(days=1000)

        except KeyError:
            pass

        # Connection to db
        db = dbConnect()
        dbCurr = db.cursor()

        # The database stores hash of hash of both email and password
        hhmail = doubleHash(email)
        hhpass = doubleHash(password)
        
        dbCurr.execute(
            "SELECT Email, Password FROM Students WHERE Email=?", (hhmail,))

        # print(f"H(H(mail)): {hhmail}")

        # TODO ew fix this
        for (mail, passwd) in dbCurr:
            if mail == hhmail:
                if passwd == hhpass:
                    session["email"] = mail
                    print("epico")
                else:
                    print("non troppo epico, ma quasi")
            else:
                print("Ao scemo registrate")

        db.close()
        # storing hash of hash of password and email in session for improved security || To implement
        return redirect(url_for("home"))

    return render_template("login.html")


@app.route("/register/", methods=["POST", "GET"])
def register():
    '''
    TODO
    '''

    if request.method == "POST":
        # get data from form
        name = request.form["name"]
        surname = request.form["surname"]
        email = request.form["email"]
        password = request.form["password"]

        # double hash password and mail
        hhmail = doubleHash(email)
        hhpass = doubleHash(password)

        # Connection to db
        db = dbConnect()
        dbCurr = db.cursor()

        dbCurr.execute("SELECT Email FROM Students WHERE Email=?", (hhmail, ))

        alreadyRegistered = False
        for _ in dbCurr:
            alreadyRegistered = True

        # Insert data to db
        try:
            if not alreadyRegistered:
                dbCurr.execute(
                    "INSERT INTO Students (Email, Password, Name, Surname) VALUES (?, ?, ?, ?)", (hhmail, hhpass, name, surname))
        except mariadb.Error as e:
            db.close()
            print(f"👿Something happended {e}")

        # commit changes to db
        db.commit()
        db.close()
        return redirect(url_for("home"))

    return render_template("register.html")


@app.route("/logout/")
def logout():
    ''' 
    Deletes all the session data
    '''
    session.clear()
    return redirect(url_for("home"))


@app.route("/dashboard/", methods=['POST', 'GET'])
def dashboard():

    # TODO check permission!
    # TODO fix file select
    # POST request in this page uploads a new video
    if request.method == 'POST':
        #
        if 'video' not in request.files:
            print('No file part')
            return redirect(request.url)
        file = request.files['video']

        # handles unselected file
        if file.filename == '':
            print('No selected file')
            return redirect(request.url)

    # TODO add progress bar
        if file and allowedFile(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        else:
            print("Non accepted extension")

    # TODO add new video to DB
    return render_template("dashboard.html")


if __name__ == '__main__':
    app.run(threaded=True)
