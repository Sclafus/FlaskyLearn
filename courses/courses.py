from flask import Blueprint, render_template, request
from utils import Utils
from dotenv import load_dotenv
from os import getenv
courses = Blueprint("courses", __name__,
                    static_folder='static', template_folder='templates')

# .env allocation
load_dotenv()
env = {
    'dbUser': getenv('DB_USER'),
    'dbPassword': getenv('DB_PASSWORD'),
    'dbHost': getenv('DB_HOST'),
    'dbPort': int(getenv('DB_PORT')),
    'dbSchema': getenv('DB_SCHEMA'),
    'uploadFolder': getenv('UPLOAD_FOLDER'),
    'videoFormats': getenv('VIDEO_FORMATS').split(', '),
}

utils = Utils(env)
db = utils.dbConnect()


@courses.route('/')
@courses.route('/home')
@courses.route('/homepage')
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
    videos = []

    dbCurr.execute(
        "SELECT lesson, description FROM Composition INNER JOIN Video WHERE Composition.courseid = ?", (courseId,))

    for elem in dbCurr:
        print(elem)
        videos.append(elem)

    return render_template('courses/course.html', videos=videos, courseId=courseId)


@courses.route('/<int:courseId>/lesson<int:lessonId>', methods=['POST', 'GET'])
def specificLesson(courseId: int, lessonId: int):
    '''Page for a specified lesson, displays video'''

    dbCurr = db.cursor()

    # getting course name
    dbCurr.execute("SELECT name FROM Course WHERE id=?", (courseId, ))
    for _courseName in dbCurr:
        courseName = _courseName[0]

    # getting video path
    dbCurr.execute(
        "SELECT path FROM Composition INNER JOIN Video on Composition.videoid = Video.id WHERE videoid = ? AND courseid=?", (lessonId, courseId))

    for _path in dbCurr:
        path = _path[0].split('/')
        videoPath = '/'.join(path[2:])
        folderPath = path[1]
        print(f"video path: {videoPath}\n folder path: {folderPath}")

    return render_template('courses/lesson.html', courseName=courseName, lessonId=lessonId, videoPath=videoPath, folderPath=folderPath)
