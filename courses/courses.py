from flask import Blueprint, render_template, request, session
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


@courses.route('/<int:courseId>/')
def specificCourse(courseId: int):
    '''Page for a specified course, dinamically generated'''

    dbCurr = db.cursor()
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

    for lesson, description in lessons:
        dbCurr.execute("SELECT timestamp FROM Visualization WHERE id=? AND email=?", (lesson, session['email']))
        if dbCurr.rowcount != 0:
            videos.append((lesson, description, True))
        else:
            videos.append((lesson, description, False))

    return render_template('courses/course.html', courseName=courseName, videos=videos, courseId=courseId)


@courses.route('/<int:courseId>/lesson<int:lessonId>', methods=['POST', 'GET'])
def specificLesson(courseId: int, lessonId: int):
    '''Page for a specified lesson, displays video'''

    dbCurr = db.cursor()

    if request.method == 'POST':
        ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        dbCurr.execute("INSERT INTO Visualization VALUES (?, ?, ?)",
                       (session['email'], lessonId, ts))

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

    return render_template('courses/lesson.html', courseName=courseName, lessonId=lessonId, videoPath=videoPath, folderPath=folderPath)


@courses.route('/<int:courseId>/quiz', methods=['POST', 'GET'])
def specificQuiz(courseId: int):
    '''Quiz for the specified course'''
    # dbCurr = db.cursor()
    # dbCurr.execute("SELECT * FROM Test INNER JOIN Question ON Test.question = Question.id INNER JOIN MadeUp ON ")
