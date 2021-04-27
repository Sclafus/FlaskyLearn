from flask import render_template, request, redirect, url_for, flash, session, abort
from flaskylearn import db, util, app, env
from datetime import timedelta


@app.route('/home')
@app.route('/homepage')
@app.route('/')
def home():
    '''Renders the homepage template'''
    return render_template('index.html')


@app.route('/login/', methods=['POST', 'GET'])
def login():
    '''Redirects to login.html. Handles POST requests to login users'''

    # NOT a post request, returning login page
    if request.method != 'POST':
        return render_template('login.html')

    # POST Request = login attempt
    email = request.form['email']
    password = request.form['password']

    # handling unchecked "Remember me" option
    try:
        stayLogged = request.form['stayLogged']
        if stayLogged:
            app.permanent_session_lifetime = timedelta(days=1000)

    except KeyError:
        pass

    # The database stores hash of hash of both email and password
    hhmail = util.doubleHash(email)
    hhpass = util.doubleHash(password)

    # Connection to db
    dbCurr = db.cursor()

    hasResult = False
    # checks if the email is present in the database
    for table in ['Student', 'Contributor']:

        dbCurr.execute(
            f"SELECT password, name FROM {table} WHERE Email=?", (hhmail,))

        for (passwd, name) in dbCurr:
            hasResult = True
            if passwd == hhpass:
                # both password and email are valid, logging in
                session['email'] = hhmail
                session['name'] = name
                print(f"User with email {hhmail} logged in successfully")
                return redirect(url_for('home'))

            # email is right, password is wrong, flashing message
            flash('Wrong password')

    # user not registered
    if not hasResult:
        flash('You are not registered')

    return redirect(request.url)


@app.route('/register/', methods=['POST', 'GET'])
def register():
    '''Register to the Student table'''

    if request.method != 'POST':
        return render_template('register.html')

    # get data from form
    name = request.form['name']
    surname = request.form['surname']
    email = request.form['email']
    password = request.form['password']

    # double hash password and mail
    hhmail = util.doubleHash(email)

    # Connection to db
    dbCurr = db.cursor()

    # checks if the email has already been used
    dbCurr.execute("SELECT email FROM Student WHERE email=?", (hhmail, ))
    alreadyRegistered = False
    for _ in dbCurr:
        alreadyRegistered = True

    # Insert data in the database
    if not alreadyRegistered:
        dbCurr.execute(
            "INSERT INTO Student (email, password, name, surname) VALUES (?, ?, ?, ?)", (hhmail, util.doubleHash(password), name, surname))
        return redirect(url_for('home'))

    # flashing message if the email is already present
    flash('This email has already been used.')
    return redirect(request.url)


@app.route('/logout/')
def logout():
    ''' Deletes all the session data'''
    session.clear()
    return redirect(url_for('home'))


@app.route('/quiz/')
def quiz():
    dbCurr = db.cursor()
    courses = {}

    # getting all the courses, using a cache to improve performance
    dbCurr.execute("SELECT name, id FROM Course")
    for courseName, courseID in dbCurr:
        courses[courseID] = courseName

    enrolled = []
    try:
        dbCurr.execute("SELECT id FROM Enrollment WHERE email=?",
                       (session['email'],))
    except KeyError:
        # user not logged in
        return abort(403)
    else:
        # getting the name of the course
        for courseID in dbCurr:
            enrolled.append(courses[courseID])

    return render_template('quiz.html', context=enrolled)
