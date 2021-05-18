from flask import Blueprint, render_template, request, session, abort, redirect, flash, url_for, jsonify, make_response
from werkzeug.utils import secure_filename
from flaskylearn import db, util, app, nullTuple

from os.path import join, isfile
from os import listdir
from datetime import datetime

dashboard = Blueprint("dashboard", __name__,
                      static_folder='static', template_folder='templates')


@dashboard.route('/', methods=['POST', 'GET'])
def homepage():
    '''Displays the dashboard only for authorized users (aka contributors)'''

    dbCurr = db.cursor()
    # Permission check
    util.requireAdminLogin()

    # getting the couses
    courses = []
    dbCurr.execute("SELECT id, name FROM Course")
    for _course in dbCurr:
        courses.append(_course)

    # GET Request
    if request.method == 'GET':
        return render_template('dashboard/dashboard.html', context=courses)

    # POST request = new video upload
    # File checks
    if 'video' not in request.files:
        return redirect(request.url)
    file = request.files['video']

    # handles unselected file
    if file.filename == '':
        flash('No file selected', category='warning')
        return redirect(request.url)

    # handles _ and space char
    if [True for match in file.filename if match in [' ', '_']]:
        flash('Please do not include _ or spaces in your file name!',
              category='warning')
        return redirect(request.url)

    newFile = False

    if file and util.allowedFile(file.filename):
        filename = secure_filename(file.filename)
        path = join(app.config['UPLOAD_FOLDER'], filename)
        files = [f for f in listdir(app.config['UPLOAD_FOLDER']) if isfile(
            join(app.config['UPLOAD_FOLDER'], f))]

        # checks if the file is already present in the filesystem
        if filename not in files:
            file.save(path)
            newFile = True
        else:
            flash('There is already a file with this name, please rename it',
                  category='warning')
    else:
        flash('The extension of the file is not allowed.', category='danger')

    description = request.form['description']

    if newFile:
        # insert new video in table
        dbCurr.execute(
            "INSERT INTO Video (description, path) VALUES (?, ?)", (description, path))

        # getting video ID
        videoId = dbCurr.lastrowid

        # getting course ID
        courseId = request.form['course']

        # insert new video in release table
        dbCurr.execute(f"INSERT INTO {util.getEnv()['dbSchema']}.Release VALUES (?, ?, ?)",
                       (session['email'], videoId, util.getTimestamp()))

        # insert new video in the course
        dbCurr.execute("INSERT INTO Composition VALUES (?, ?, ?)",
                       (videoId, courseId, int(request.form['lessonNum'])))

    return redirect(request.url)


@dashboard.route('/newCourse', methods=['POST', 'GET'])
def newCourse():
    '''Adds new course to the database'''
    dbCurr = db.cursor()

    # permission check
    util.requireAdminLogin()

    if request.method == 'GET':
        return render_template('dashboard/newCourse.html')

    name = request.form['name']
    duration = request.form['time']
    description = request.form['description']
    dbCurr.execute(
        'INSERT INTO Course (name, duration, description) VALUES (?, ?, ?)', (name, duration, description))
    return redirect(url_for('dashboard.homepage'))


@dashboard.route('/newQuiz', methods=['POST', 'GET'])
def newQuiz():
    '''returns the page where you can create a quiz for your course'''
    dbCurr = db.cursor()
    # permission check
    util.requireAdminLogin()

    # GET Request
    if request.method == 'GET':
        # getting courses
        courses = {}
        # selecting only the courses that don't have a Test
        dbCurr.execute(
            "SELECT id, name FROM Course WHERE id NOT IN (SELECT courseid FROM Test)")
        for courseId, courseName in dbCurr:
            courses[courseId] = courseName
        return render_template('dashboard/newQuiz.html', courses=courses)

    # POST Request
    if request.method == 'POST':
        # Getting data
        quiz = request.get_json()

        # Adding questions and answers
        for question in quiz['questions']:

            # adding the question
            dbCurr.execute("INSERT INTO Question (topic) VALUES (?)",
                           (question['question'], ))

            # getting the question id back
            questionId = dbCurr.lastrowid

            # adding the question to the Test table
            dbCurr.execute("INSERT INTO Test (courseid, questionid) VALUES (?, ?)",
                           (quiz['course'], questionId))

            # adding the answers for the question
            for answer in question['answers']:
                # adding the answer in the Answer table
                dbCurr.execute(
                    "INSERT INTO Answer (topic) VALUES (?)", (answer['answer'], ))
                answerId = dbCurr.lastrowid

                # adding the answer and question in the MadeUp table
                dbCurr.execute("INSERT INTO MadeUp VALUES (?, ?, ?)",
                               (questionId, answerId, answer['correct']))

        # Getting the response back
        response = make_response(
            jsonify({'message': 'The quiz has been submitted correctly!'}), 200)
        flash("The quiz has been submitted correctly!", category='success')
        return response
