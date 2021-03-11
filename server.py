from flask import Flask, redirect, url_for, render_template, request, session
from os import environ
from datetime import timedelta
from passlib.hash import sha256_crypt
# from dotenv import load_dotenv

app = Flask(__name__)
# TODO .env secretkey
# TODO set session duration
# app.secret_key = sha256_crypt.hash(environ['SECRET_KEY']) 
app.secret_key = "development"

@app.route("/")
def home():
  '''
  Displays the homepage, stored in index.html
  '''
  return render_template("index.html")

@app.route("/login/", methods=["POST", "GET"])
def login():
  '''
  Redirects to login.html 
  Handles POST requests to login users
  '''
  if request.method == "POST":
    #using hash of email and password for improved security
    email = sha256_crypt.hash(request.form["email"])
    password = sha256_crypt.hash(request.form["password"])

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

    #storing hash of hash of password and email in session for improved security
    session["email"] = emailFromDB 
    session["password"] = passwordFromDB
    return redirect(url_for("home"))

  return render_template("login.html")

@app.route("/register/", methods=["POST", "GET"])
def register():
  return render_template("register.html")

if __name__ == '__main__':
  app.run(threaded=True)