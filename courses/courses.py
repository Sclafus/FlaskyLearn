from flask import Blueprint, render_template, request
from utils import Utils 
from dotenv import load_dotenv
import os
courses = Blueprint("courses", __name__, static_folder='static', template_folder='templates')

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
def homepage():
    '''courses homepage, card style'''
    dbCurr = db.cursor()
    courses = []

    dbCurr.execute("SELECT name, duration, description FROM Course")
    for name, duration, description in dbCurr:
        courses.append((name, duration, description))
    return render_template('courses.html', context=courses)

@courses.route('/<courseName>/', methods=['POST', 'GET'])
def course(courseName):
    '''Page for a specified course, dinamically generated'''
    dbCurr = db.cursor()
    videos = []
    dbCurr.execute("SELECT * FROM Composition INNER JOIN Video INNER JOIN Course WHERE Course.name = ?", (courseName,))
    print("working")
    for i, elem in enumerate(dbCurr):
        print(f"{i}  --- {elem}")

    if request.method != 'POST':
        return render_template('course.html', context=videos)