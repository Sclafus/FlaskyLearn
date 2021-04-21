from flask import Flask, redirect, url_for, render_template, request, session, flash, abort
from werkzeug.utils import secure_filename
from datetime import timedelta, datetime
from Crypto.Hash import SHA3_256
from dotenv import load_dotenv
import mariadb
import os
from utils import Utils
from courses.courses import courses

# loading .env file
load_dotenv()
secretKey = os.getenv('SECRET_KEY')

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
app.register_blueprint(courses, url_prefix='/courses')
util = Utils(env)


# Error handlers


@app.errorhandler(403)
def forbidden(e):
    '''Error page for 403 forbidden http error'''
    return render_template('403.html'), 403


@app.errorhandler(404)
def not_found(e):
    '''Error page for 404 not found http error'''
    return render_template('404.html'), 404


db = util.dbConnect()


@app.route('/')
def home():
    '''Renders the homepage template'''
    return render_template('index.html')


@app.route('/login/', methods=['POST', 'GET'])
def login():
    '''Redirects to login.html. Handles POST requests to login users'''

    # NOT a post request, returning login page
    if request.method != 'POST':
        return render_template('login.html')

    # POST Request = login attempt
    email = request.form['email']
    password = request.form['password']

    # handling unchecked "Remember me" option
    try:
        stayLogged = request.form['stayLogged']
        if stayLogged:
            app.permanent_session_lifetime = timedelta(days=1000)

    except KeyError:
        pass

    # The database stores hash of hash of both email and password
    hhmail = util.doubleHash(email)
    hhpass = util.doubleHash(password)

    # Connection to db
    dbCurr = db.cursor()

    hasResult = False
    # checks if the email is present in the database
    for table in ['Student', 'Contributor']:

        dbCurr.execute(
            f"SELECT password, name FROM {table} WHERE Email=?", (hhmail,))

        for (passwd, name) in dbCurr:
            hasResult = True
            if passwd == hhpass:
                # both password and email are valid, logging in
                session['email'] = hhmail
                session['name'] = name
                print(f"User with email {hhmail} logged in successfully")
                return redirect(url_for('home'))

            # email is right, password is wrong, flashing message
            flash('Wrong password')

    # user not registered
    if not hasResult:
        flash('You are not registered')


@app.route('/register/', methods=['POST', 'GET'])
def register():
    '''Register to the Student table'''

    if request.method != 'POST':
        return render_template('register.html')

    # get data from form
    name = request.form['name']
    surname = request.form['surname']
    email = request.form['email']
    password = request.form['password']

    # double hash password and mail
    hhmail = util.doubleHash(email)

    # Connection to db
    dbCurr = db.cursor()

    # checks if the email has already been used
    dbCurr.execute("SELECT email FROM Student WHERE email=?", (hhmail, ))
    alreadyRegistered = False
    for _ in dbCurr:
        alreadyRegistered = True

    # Insert data in the database
    if not alreadyRegistered:
        dbCurr.execute(
            "INSERT INTO Student (email, password, name, surname) VALUES (?, ?, ?, ?)", (hhmail, util.doubleHash(password), name, surname))
        return redirect(url_for('home'))

    # flashing message if the email is already present
    flash('This email has already been used.')


@app.route('/logout/')
def logout():
    ''' Deletes all the session data'''
    session.clear()
    return redirect(url_for('home'))


@app.route('/dashboard/', methods=['POST', 'GET'])
def dashboard():
    '''Displays the dashboard only for authorized users (aka contributors)'''

    authorized = False

    # checks if the user is authenticated
    if 'email' in session:
        dbCurr = db.cursor()
        dbCurr.execute("SELECT email FROM Contributor WHERE Email=?",
                       (session['email'], ))

        # let's check if the user is authenticated
        for _ in dbCurr:
            authorized = True

    if not authorized:
        # if not authorized, forbidden
        return abort(403)

    # AUTHORIZED

    if request.method != 'POST':
        # getting the couses available
        courses = []
        dbCurr.execute("SELECT name FROM Course")
        for courseName in dbCurr:
            courses.append(courseName[0])
        return render_template('dashboard.html', context=courses)

    # POST request = new video upload

    # File checks
    if 'video' not in request.files:
        print('No file part')
        return redirect(request.url)
    file = request.files['video']

    # handles unselected file
    if file.filename == '':
        print('No selected file')
        return redirect(request.url)

    # handles _ char
    if '_' in file.filename:
        print('Pls no underscores in filename uwu')
        return redirect(request.url)

    if file and util.allowedFile(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    else:
        print('Non accepted extension')

    description = request.form['description']

    path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

    # insert new video in table
    dbCurr.execute(
        "INSERT INTO Video (description, path) VALUES (?, ?)", (description, path))

    # getting video ID
    dbCurr.execute(
        "SELECT id FROM Video WHERE description=? AND path=?", (description, path))
    for _videoIDTuple in dbCurr:
        videoID = _videoIDTuple[0]

    # getting course ID
    dbCurr.execute("SELECT id FROM Course WHERE name=?",
                   (request.form['course'],))
    for _courseIDTuple in dbCurr:
        courseID = _courseIDTuple[0]

    # insert new video in release table

    ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    dbCurr.execute("INSERT INTO flaskylearn.Release VALUES (?, ?, ?)",
                   (session['email'], videoID, ts))

    # insert new video in the course
    dbCurr.execute("INSERT INTO Composition VALUES (?, ?, ?)",
                   (videoID, courseID, int(request.form['lessonNum'])))


@app.route('/newCourse/', methods=['POST', 'GET'])
def newCourse():
    '''Adds new course to the database'''
    authorized = False
    if 'email' in session:
        dbCurr = db.cursor()
        dbCurr.execute(
            'SELECT email FROM Contributor WHERE email=?', (session['email'],))
        for _ in dbCurr:
            authorized = True
    else:
        return abort(403)

    if not authorized:
        return abort(403)

    if request.method != 'POST':
        return render_template('newCourse.html')

    name = request.form['name']
    duration = request.form['time']
    dbCurr.execute(
        'INSERT INTO Course (name, duration) VALUES (?,?)', (name, duration))
    return redirect(url_for('dashboard'))


@app.route('/quiz/')
def quiz():
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
    app.run(debug=True, threaded=True)
