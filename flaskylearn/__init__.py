from dotenv import load_dotenv
from os import getenv
from flask import Flask
from flaskylearn.utils import Utils
from Crypto.Hash import SHA3_256

# loading .env file
load_dotenv()
secretKey = getenv('SECRET_KEY')

# .env allocation
env = {
    'dbUser': getenv('DB_USER'),
    'dbPassword': getenv('DB_PASSWORD'),
    'dbHost': getenv('DB_HOST'),
    'dbPort': int(getenv('DB_PORT')),
    'dbSchema': getenv('DB_SCHEMA'),
    'uploadFolder': getenv('UPLOAD_FOLDER'),
    'videoFormats': getenv('VIDEO_FORMATS').split(', '),
}

# Flask inizialization
app = Flask(__name__)
app.secret_key = SHA3_256.new(secretKey.encode()).hexdigest()

# upload folder for videos
app.config['UPLOAD_FOLDER'] = env['uploadFolder']


# utils obj and db connection
util = Utils(env)
db = util.dbConnect()

from flaskylearn import routes
from courses.courses import courses
from errors.errors import errors
from dashboard.dashboard import dashboard

# blueprints initialization
app.register_blueprint(courses, url_prefix='/courses')
app.register_blueprint(dashboard, url_prefix='/dashboard')
app.register_blueprint(errors)