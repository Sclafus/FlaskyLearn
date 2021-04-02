from flask import Flask, redirect, url_for, render_template, request, session, flash
from werkzeug.utils import secure_filename
from datetime import timedelta
from Crypto.Hash import SHA3_256
from dotenv import load_dotenv
import mariadb
import os
import re

# loading .env file
load_dotenv()
secretKey = os.getenv("SECRET_KEY")

# .env allocation
env = {
    'dbUser' : os.getenv('DB_USER'),
    'dbPassword' : os.getenv('DB_PASSWORD'),
    'dbHost' : os.getenv('DB_HOST'),
    'dbPort' : int(os.getenv('DB_PORT')),
    'dbSchema' : os.getenv('DB_SCHEMA'),
    'uploadFolder' : os.getenv('UPLOAD_FOLDER'),
    'videoFormats' : os.getenv('VIDEO_FORMATS').split(', '),
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


@app.route("/")
def home():
    '''
    Renders the homepage template
    '''
    # try:
    #     print(f"EMAIL: {session['email']}")
    # except KeyError:
    #     print("no session data")

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
                    else:
                        print(f"Wrong Password for email {hhmail}")

        db.close()
        return redirect(url_for("home"))

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
            # TODO check the name of the file for _

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

            # TODO add progress bar
            if file and allowedFile(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            else:
                print("Non accepted extension")
                db.close()

            description = request.form['description']
            path = f"videos/{filename}"

            dbCurr.execute(
                "INSERT INTO Video (description, path) VALUES (?, ?)", (description, path))
            db.commit()
            db.close()

        return render_template("dashboard.html")

    # if not authorized, forbidden
    return redirect(url_for("forbidden")), 403


@app.route("/forbidden/")
def forbidden():
    '''
    Renders the forbidden template
    '''
    return render_template("forbidden.html")


@app.route("/courses/")
def courses():

    # database connection
    db = dbConnect()
    dbCurr = db.cursor()
    courses = []

    # checks if user is authenticated
    dbCurr.execute("SELECT name, time FROM Course ")
    for courseName, courseTime in dbCurr:
        courses.append((courseName, courseTime))

    print(f"{courses}")
    # pass the list of Courses IDs that the student is enrolled. Contributors can see all the courses
    render_template('courses.html', context=courses)

@app.route('/newCourse/', methods=['POST', 'GET'])
def newCourse():
    authorized = False
    if 'email' in session:
        db = dbConnect()
        dbCurr = db.cursor()
        dbCurr.execute('SELECT email FROM Contributor WHERE email=?', (session['email'],))
        for _ in dbCurr:
            authorized = True
    else:
        return redirect(url_for('login'))

    if authorized:  
        if request.method == 'POST':
            name = request.form['name']
            time = request.form['time']
            dbCurr.execute('INSERT INTO Course (name, time) VALUES (?,?)', (name, time))
            db.commit()
            db.close()
            return redirect(url_for('dashboard'))

        return render_template('newCourse.html')
    return redirect(url_for('forbidden'), 403)

if __name__ == '__main__':
    app.run(threaded=True)