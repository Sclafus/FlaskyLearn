from flask import Flask, redirect, url_for, render_template, request, session, flash, abort
from werkzeug.utils import secure_filename
from datetime import timedelta, datetime
from Crypto.Hash import SHA3_256
from dotenv import load_dotenv
from functools import lru_cache
import mariadb
import os
import re

# loading .env file
load_dotenv()
secretKey = os.getenv("SECRET_KEY")

# .env allocation
env = {
    'dbUser': os.getenv('DB_USER'),
    'dbPassword': os.getenv('DB_PASSWORD'),
    'dbHost': os.getenv('DB_HOST'),
    'dbPort': int(os.getenv('DB_PORT')),
    'dbSchema': os.getenv('DB_SCHEMA'),
    'uploadFolder': os.getenv('UPLOAD_FOLDER'),
    'videoFormats': os.getenv('VIDEO_FORMATS').split(', '),
}

# Flask inizialization
app = Flask(__name__)
app.secret_key = SHA3_256.new(secretKey.encode()).hexdigest()
app.config['UPLOAD_FOLDER'] = env['uploadFolder']


def doubleHash(toBeHashed: str) -> str:
    '''
    return the double hash of the input string
    '''
    return SHA3_256.new((SHA3_256.new(toBeHashed.encode()).hexdigest()).encode()).hexdigest()


def dbConnect():
    '''
    Returns connection to the local database object
    '''
    try:
        conn = mariadb.connect(
            user=env['dbUser'],
            password=env['dbPassword'],
            host=env['dbHost'],
            port=env['dbPort'],
            database=env['dbSchema']
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
    if ext in env['videoFormats']:
        return True
    return False

# Error handlers

@app.errorhandler(403)
def forbidden(e):
    '''
    Error page for 403 forbidden http error
    '''
    return render_template("403.html"), 403


@app.errorhandler(404)
def not_found(e):
    '''
    Error page for 404 not found http error
    '''
    return render_template('404.html'), 404


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

        # The database stores hash of hash of both email and password
        hhmail = doubleHash(email)
        hhpass = doubleHash(password)

        # Connection to db
        db = dbConnect()
        dbCurr = db.cursor()
        flag = False

        for table in ["Student", "Contributor"]:

            if not flag:
                dbCurr.execute(
                    f"SELECT password, name FROM {table} WHERE Email=?", (hhmail,))

                for (passwd, name) in dbCurr:
                    flag = True
                    if passwd == hhpass:
                        session["email"] = hhmail
                        session["name"] = name
                        print(
                            f"User with email {hhmail} logged in successfully")
                        return redirect(url_for("home"))
                    else:
                        flash("Wrong password")
                        print(f"Wrong Password for email {hhmail}")

        db.close()

    return render_template("login.html")


@app.route("/register/", methods=["POST", "GET"])
def register():
    '''
    Register to the Student table
    '''

    if request.method == "POST":
        # get data from form
        name = request.form["name"]
        surname = request.form["surname"]
        email = request.form["email"]
        password = request.form["password"]

        # double hash password and mail
        hhmail = doubleHash(email)
        # Connection to db
        db = dbConnect()
        dbCurr = db.cursor()

        dbCurr.execute("SELECT email FROM Student WHERE email=?", (hhmail, ))

        alreadyRegistered = False
        for _ in dbCurr:
            alreadyRegistered = True

        # Insert data to db
        try:
            if not alreadyRegistered:
                dbCurr.execute(
                    "INSERT INTO Student (email, password, name, surname) VALUES (?, ?, ?, ?)", (hhmail, doubleHash(password), name, doubleHash(surname)))
                db.commit()
                return redirect(url_for("home"))  
            else:
                flash("This email has already been used.")
        except mariadb.Error as e:
            db.close()
            print(f"👿Something happended {e}")

        # commit changes to db
        db.close()

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
    '''
    Displays the dashboard only for authorized users (aka contributors)
    '''

    authorized = False

    if 'email' in session:
        db = dbConnect()
        dbCurr = db.cursor()
        dbCurr.execute("SELECT email FROM Contributor WHERE Email=?",
                       (session['email'], ))

        # is there a better way to do this?
        for _ in dbCurr:
            authorized = True

    # POST request in this page uploads a new video
    if authorized:

        if (request.method == 'POST'):

            # File checks
            if 'video' not in request.files:
                print('No file part')
                db.close()
                return redirect(request.url)
            file = request.files['video']

            # handles unselected file
            if file.filename == '':
                print('No selected file')
                db.close()
                return redirect(request.url)

            # handles _ char
            if '_' in file.filename:
                print('Pls no underscores in filename uwu')
                db.close()
                return redirect(request.url)

            if file and allowedFile(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            else:
                print("Non accepted extension")
                db.close()

            description = request.form['description']

            # maybe improve this?
            path = f"videos/{filename}"
            print(request.form)

            # insert new video in table 
            dbCurr.execute(
                "INSERT INTO Video (description, path) VALUES (?, ?)", (description, path))
            db.commit()


            # getting video ID
            dbCurr.execute("SELECT id FROM Video WHERE description=? AND path=?", (description, path))
            for _videoIDTuple in dbCurr:
                videoID = _videoIDTuple[0]
                
            # TODO FIX ME adding to Release table 
            # now = datetime.now()
            # timestamp = now.strftime('%Y-%m-%d %H:%M:%S')
            # print(f"--------{timestamp}---------")
            # dbCurr.execute("INSERT INTO Release (email, id, timestamp) VALUES (?, ?, ?)", (session['email'], videoID, timestamp))
            
            #getting course ID
            dbCurr.execute("SELECT id FROM Course WHERE name=?", (request.form['course'],))
            for _courseIDTuple in dbCurr:
                courseID = _courseIDTuple[0]

            # adding the video to the course
            dbCurr.execute("INSERT INTO Composition (videoid, courseid, lesson) VALUES (?, ?, ?)", (videoID, courseID, int(request.form['lessonNum'])))
            db.commit()

        courses = []
        dbCurr.execute("SELECT name FROM Course")
        for courseName in dbCurr:
            courses.append(courseName[0])
        db.close()
        return render_template("dashboard.html", context=courses)

    # if not authorized, forbidden
    return abort(403)


@app.route("/courses/")
def courses():

    # database connection
    db = dbConnect()
    dbCurr = db.cursor()
    courses = []

    # checks if user is authenticated
    dbCurr.execute("SELECT name, time FROM Course")
    for courseName, courseTime in dbCurr:
        courses.append((courseName, courseTime))

    return render_template('courses.html', context=courses)


@app.route('/newCourse/', methods=['POST', 'GET'])
def newCourse():
    authorized = False
    if 'email' in session:
        db = dbConnect()
        dbCurr = db.cursor()
        dbCurr.execute(
            'SELECT email FROM Contributor WHERE email=?', (session['email'],))
        for _ in dbCurr:
            authorized = True
    else:
        return abort(403)

    if authorized:
        if request.method == 'POST':
            name = request.form['name']
            time = request.form['time']
            dbCurr.execute(
                'INSERT INTO Course (name, time) VALUES (?,?)', (name, time))
            db.commit()
            db.close()
            return redirect(url_for('dashboard'))

        return render_template('newCourse.html')
    return abort(403)


@lru_cache
@app.route('/quiz/')
def quiz():
    db = dbConnect()
    dbCurr = db.cursor()
    courses = {}

    # getting all the courses, using a cache to improve performance
    dbCurr.execute("SELECT name, id FROM Course")
    for courseName, courseID in dbCurr:
        courses[courseID] = courseName

    enrolled = []
    try:
        dbCurr.execute("SELECT id FROM Enrollment WHERE email=?",
                       (session['email'],))
    except KeyError:
        # user not logged in
        return abort(403)
    else:
        # getting the name of the course
        for courseID in dbCurr:
            enrolled.append(courses[courseID])

    return render_template('quiz.html', context=enrolled)


if __name__ == '__main__':
    app.run(threaded=True)