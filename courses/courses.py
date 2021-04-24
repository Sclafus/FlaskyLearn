from flask import Blueprint, render_template, request
from utils import Utils
from dotenv import load_dotenv
import os
courses = Blueprint("courses", __name__,
                    static_folder='static', template_folder='templates')

# .env allocation
load_dotenv()
env = {
    'dbUser': os.getenv('DB_USER'),
    'dbPassword': os.getenv('DB_PASSWORD'),
    'dbHost': os.getenv('DB_HOST'),
    'dbPort': int(os.getenv('DB_PORT')),
    'dbSchema': os.getenv('DB_SCHEMA'),
    'uploadFolder': os.getenv('UPLOAD_FOLDER'),
    'videoFormats': os.getenv('VIDEO_FORMATS').split(', '),
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
    return render_template('courses.html', context=courses)


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

    return render_template('course.html', videos=videos, courseId=courseId)

@courses.route('/<int:courseId>/lesson=<int:lessonId>', methods=['POST', 'GET'])
def specificLesson(courseId: int, lessonId: int):
    pass