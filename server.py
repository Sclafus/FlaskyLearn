from flask import Flask, redirect, url_for, render_template, request, session
from datetime import timedelta
from passlib.hash import sha256_crypt
from dotenv import load_dotenv
import mariadb
import os

#loading .env file
load_dotenv()
secretKey = os.getenv("SECRET_KEY")
dbUser = os.getenv("DB_USER")
dbPassword = os.getenv("DB_PASSWORD")
dbHost = os.getenv("DB_HOST")
dbPort = int(os.getenv("DB_PORT"))
dbSchema = os.getenv("DB_SCHEMA")


app = Flask(__name__)
app.secret_key = sha256_crypt.hash(secretKey)

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
    return (conn.cursor())

  except mariadb.Error as e:
    print(f"Error connecting to MariaDB Platform: {e}")
    raise Exception

@app.route("/")
def home():
  '''
  Displays the homepage, stored in index.html
  '''
  try:
    user = session["email"]
    return render_template("index.html", name=user)

  except KeyError:
    pass
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

    # TODO access database and check if the user data is correct
    emailFromDB = email
    passwordFromDB = password

    #storing hash of hash of password and email in session for improved security || To implement
    session["email"] = emailFromDB
    return redirect(url_for("home"))

  return render_template("login.html")

@app.route("/register/", methods=["POST", "GET"])
def register():
  return render_template("register.html")

@app.route("/logout/")
def logout():
  ''' 
  Deletes all the session data
  '''
  session.clear()
  return redirect(url_for("home"))

if __name__ == '__main__':
  app.run(threaded=True)