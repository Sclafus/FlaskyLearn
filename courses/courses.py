from flask import Blueprint, render_template, request, session, flash, redirect, url_for
from flaskylearn import db, util
from datetime import datetime
courses = Blueprint("courses", __name__,
                    static_folder='static', template_folder='templates')


@courses.route('/')
def homepage():
    '''courses homepage, card style'''
    dbCurr = db.cursor()
    courses = []

    dbCurr.execute("SELECT * FROM Course")
    for courseid, name, duration, description in dbCurr:
        courses.append((courseid, name, duration, description))
    return render_template('courses/courses.html', context=courses)


@courses.route('/<int:courseId>/', methods=['POST', 'GET'])
def specificCourse(courseId: int):
    '''Page for a specified course, dinamically generated'''
    dbCurr = db.cursor()

    # POST request = a user is trying to enroll in the course
    if request.method == 'POST':
        dbCurr.execute("INSERT INTO Enrollment VALUES (?, ?, ?)", (session['email'], courseId, util.getTimestamp()))
        flash("You have been enrolled successfully", category='success')
        return redirect(request.url)

    # GET request
    lessons = []
    videos = []
    # getting course name
    dbCurr.execute("SELECT name FROM Course WHERE id=?", (courseId, ))
    for _courseName in dbCurr:
        courseName = _courseName[0]

    # Getting all the lessons for the specified course
    dbCurr.execute(
        "SELECT DISTINCT lesson, description FROM Composition INNER JOIN Video ON Video.id = Composition.videoid WHERE Composition.courseid = ?", (courseId,))

    for lesson, description in dbCurr:
        lessons.append((lesson, description))

    # checking if the lesson has already been viewed
    for lesson, description in lessons:
        flag = False

        try:
            dbCurr.execute(
                "SELECT id FROM Visualization WHERE id=? AND email=?", (lesson, session['email']))
            for _ in dbCurr:
                flag = True
        except KeyError:
            # user not logged in
            pass

        videos.append((lesson, description, flag))

    # checking if the user is already enrolled
    try:
        session['enrolled'] = False
        dbCurr.execute(
            "SELECT timestamp FROM Enrollment WHERE email=? AND id=?", (session['email'], courseId))

        for _ in dbCurr:
            session['enrolled'] = True
        
    except KeyError:
        # user not logged in, enrollment is not applicable
        session['enrolled'] = None
    
    # checks if the user has seen all the lessons or not
    notViewedVideos = [video for video in videos if not video[2]] 
    quizAvailable = True if not notViewedVideos else False
    if quizAvailable: 
        flash("Congratulations, you have finished the course! You can take a brief quiz to obtain your certificate", category='success')
    return render_template('courses/course.html', courseName=courseName, videos=videos, courseId=courseId, quizAvailable=quizAvailable)


@courses.route('/<int:courseId>/lesson<int:lessonId>', methods=['GET', 'POST'])
def specificLesson(courseId: int, lessonId: int):
    '''Page for a specified lesson, displays video'''

    # user is not logged in
    if not 'email' in session:
        flash("You need to login in order to see this lesson", category='warning')
        return redirect(url_for('courses.specificCourse', courseId=courseId))

    dbCurr = db.cursor()

    # POST Request
    if request.method == 'POST':

        if 'admin' in session:
            flash("Contributors can't mark videos as played", category='warning')
            return redirect(request.url)

        # getting back the videoid
        dbCurr.execute(
            "SELECT videoid FROM Composition WHERE courseid=? AND lesson=?", (courseId, lessonId))
        for _videoid in dbCurr:
            videoId = _videoid[0]

        # marking the video as played for a student
        ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        dbCurr.execute("INSERT INTO Visualization (email, id, timestamp) VALUES (?, ?, ?)",
                       (session['email'], videoId, ts))
        flash("The video has been marked as played", category='success')
        return redirect(request.url)

    # GET Request
    # getting course name
    dbCurr.execute("SELECT name FROM Course WHERE id=?", (courseId, ))
    for _courseName in dbCurr:
        courseName = _courseName[0]

    # getting video path
    dbCurr.execute(
        "SELECT path FROM Composition INNER JOIN Video on Composition.videoid = Video.id WHERE videoid = ? AND courseid=?", (lessonId, courseId))

    for _path in dbCurr:
        path = _path[0].split('/')
        videoPath = '/'.join(path[-2:])
        folderPath = path[-3]

    return render_template('courses/lesson.html', courseName=courseName, lessonId=lessonId, videoPath=videoPath, folderPath=folderPath, courseId=courseId)


@courses.route('/<int:courseId>/quiz', methods=['POST', 'GET'])
def specificQuiz(courseId: int):
    '''Quiz for the specified course'''
    return render_template("courses/quiz.html")
    # dbCurr = db.cursor()
    # dbCurr.execute("SELECT * FROM Test INNER JOIN Question ON Test.question = Question.id INNER JOIN MadeUp ON ")
