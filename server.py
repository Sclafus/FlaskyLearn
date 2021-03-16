from flask import Flask, redirect, url_for, render_template, request, session, flash
from werkzeug.utils import secure_filename
from datetime import timedelta
from passlib.hash import sha256_crypt
from dotenv import load_dotenv
import mariadb
import os
import re

#loading .env file
load_dotenv()
secretKey = os.getenv("SECRET_KEY")

dbUser = os.getenv("DB_USER")
dbPassword = os.getenv("DB_PASSWORD")
dbHost = os.getenv("DB_HOST")
dbPort = int(os.getenv("DB_PORT"))
dbSchema = os.getenv("DB_SCHEMA")
uploadFolder = os.getenv("UPLOAD_FOLDER")

# TODO add to .env
# ALLOWED_EXTENSIONS = {'webm', 'mkv', 'flv', 'avi', 'mov', 'wmv', 'mp4', 'm4v', '3gp'}

app = Flask(__name__)
app.secret_key = sha256_crypt.hash(secretKey)
app.config['UPLOAD_FOLDER'] = uploadFolder

def dbConnect():
  '''
  Returns connection to the local database object
  '''
  try:
    conn = mariadb.connect(
      user = dbUser,
      password = dbPassword,
      host = dbHost,
      port = dbPort,
      database = dbSchema
    )
    return conn

  except mariadb.Error as e:
    print(f"Error connecting to MariaDB Platform: {e}")
    raise Exception

@app.route("/")
def home():
  '''
  Displays the homepage, stored in index.html
  '''
  # try:
  #   user = session["email"]

  # except KeyError:
  #   #TODO ew
  #   pass
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

    #handling unchecked "Remember me" option
    try:
      stayLogged = request.form["stayLogged"]
      if stayLogged:
        app.permanent_session_lifetime = timedelta(days=1000)
    
    except KeyError:
      pass
    
    # Connection to db
    db = dbConnect()
    dbCurr = db.cursor()

    hhmail = sha256_crypt.hash(sha256_crypt.hash(email))
    hhpass = sha256_crypt.hash(sha256_crypt.hash(password))

    # The database stores hash of hash of both email and password 
    dbCurr.execute("SELECT Email, Password FROM Students WHERE Email=?", (hhmail,))

    print(f"H(H(mail)): {hhmail}")

    # TODO ew fix this
    for (mail, passwd) in dbCurr:
      if mail == hhmail:
        if passwd == hhpass:
          session["email"] = mail
          print("epico")
        else:
          print("non troppo epico, ma quasi")
      else:
        print("Ao scemo registrate")

    db.close()
    #storing hash of hash of password and email in session for improved security || To implement
    return redirect(url_for("home"))

  return render_template("login.html")

@app.route("/register/", methods=["POST", "GET"])
def register():
  '''
  TODO
  '''

  if request.method == "POST":
    #get data from form
    name = request.form["name"]
    surname = request.form["surname"]
    email = request.form["email"]
    password = request.form["password"]

    #double hash password and mail
    hhmail = sha256_crypt.hash(sha256_crypt.hash(email))
    hhpass = sha256_crypt.hash(sha256_crypt.hash(password))
    print(f"H(H(mailRegister)): {hhmail}")
    # Connection to db
    db = dbConnect()
    dbCurr = db.cursor()

    # Insert data to db
    try:
      dbCurr.execute("INSERT INTO Students (Email, Password, Name, Surname) VALUES (?, ?, ?, ?)", (hhmail, hhpass, name, surname))
    except mariadb.Error as e:
      db.close()
      print(f"👿Something happended {e}")

    #commit changes to db
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

  #TODO check on extensions
  #TODO fix file select
  #TODO add progress bar
  if request.method == 'POST':
    if 'video' not in request.files:
      print('No file part')
      return redirect(request.url)
    file = request.files['video']

    if file.filename == '':
      print('No selected file')
      return redirect(request.url)

    if file:
      filename = secure_filename(file.filename)
      file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
  return render_template("dashboard.html")

if __name__ == '__main__':
  app.run(threaded=True)