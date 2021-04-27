from flask import Blueprint, render_template, request, session, abort, redirect, flash,url_for
from werkzeug.utils import secure_filename
from flaskylearn import db, util, app

from os.path import join, isfile
from os import listdir
from datetime import datetime

dashboard = Blueprint("dashboard", __name__,
                    static_folder='static', template_folder='templates')

@dashboard.route('/', methods=['POST', 'GET'])
def homepage():
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
        return render_template('dashboard/dashboard.html', context=courses)

    # POST request = new video upload

    # File checks
    if 'video' not in request.files:
        return redirect(request.url)
    file = request.files['video']

    # handles unselected file
    if file.filename == '':
        flash('No file selected')
        return redirect(request.url)

    # handles _ char
    if '_' in file.filename:
        flash('Please do not include _ in your file name')
        return redirect(request.url)

    if file and util.allowedFile(file.filename):
        filename = secure_filename(file.filename)
        path = join(app.config['UPLOAD_FOLDER'], filename)
        files = [f for f in listdir(app.config['UPLOAD_FOLDER']) if isfile(
            join(app.config['UPLOAD_FOLDER'], f))]

        # checks if the file is already present in the filesystem
        if filename not in files:
            file.save(path)
        else:
            flash('There is already a file with this name, please rename it')
    else:
        flash('The extension of the file is not allowed.')

    description = request.form['description']

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

    dbCurr.execute(f"INSERT INTO {util.getEnv()['dbSchema']}.Release VALUES (?, ?, ?)",
                   (session['email'], videoID, ts))

    # insert new video in the course
    dbCurr.execute("INSERT INTO Composition VALUES (?, ?, ?)",
                   (videoID, courseID, int(request.form['lessonNum'])))
    
    return redirect(request.url)

@dashboard.route('/newCourse/', methods=['POST', 'GET'])
def newCourse():
    '''Adds new course to the database'''
    authorized = False
    if 'email' in session:
        dbCurr = db.cursor()
        dbCurr.execute(
            'SELECT email FROM Contributor WHERE email=?', (session['email'],))
        for _ in dbCurr:
            authorized = True

    if ((not authorized) or ('email' not in session)):
        return abort(403)

    if request.method != 'POST':
        return render_template('dashboard/newCourse.html')

    name = request.form['name']
    duration = request.form['time']
    description = request.form['description']
    dbCurr.execute(
        'INSERT INTO Course (name, duration, description) VALUES (?, ?, ?)', (name, duration, description))
    return redirect(url_for('homepage'))