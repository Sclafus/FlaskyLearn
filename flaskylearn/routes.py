from flask import render_template, request, redirect, url_for, flash, session, abort
from flaskylearn import db, util, app, env, nullTuple
from datetime import timedelta


@app.route('/home')
@app.route('/homepage')
@app.route('/')
def home():
    '''Renders the homepage template'''
    dbCurr = db.cursor()
    dbCurr.execute("SELECT EXISTS(SELECT * FROM Answer)")
    if dbCurr.next() != nullTuple:
        print('a')
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
            f"SELECT password, name, surname FROM {table} WHERE email=?", (hhmail,))

        for passwd, name, surname in dbCurr:
            hasResult = True
            if passwd == hhpass:
                # both password and email are valid, logging in
                session['email'] = hhmail
                session['name'] = name
                session['surname'] = surname
                if table == 'Contributor':
                    session['admin'] = True
                print(f"User with email {hhmail} logged in successfully")
                return redirect(url_for('home'))

            # email is right, password is wrong, flashing message
            flash('Wrong password', category='danger')

    # user not registered
    if not hasResult:
        flash('You are not registered', category='warning')

    return redirect(request.url)


@app.route('/register/', methods=['POST', 'GET'])
def register():
    '''Register to the Student table'''

    if request.method == 'GET':
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
    alreadyRegistered = False
    for table in ['Student', 'Contributor']:
        dbCurr.execute(f"SELECT EXISTS(SELECT email FROM {table} WHERE email=?)", (hhmail, ))
        if dbCurr.next() != (0,):
            alreadyRegistered = True

    if alreadyRegistered:
        # flashing message if the email is already present
        flash('This email has already been used.', category='warning')
        return redirect(request.url)

    # Insert new Student in the database
    dbCurr.execute(
        "INSERT INTO Student VALUES (?, ?, ?, ?)", (hhmail, name, surname, util.doubleHash(password)))
    flash("You have been registered. You can now login!", category='success')
    return redirect(url_for('login'))


@app.route('/logout/')
def logout():
    ''' Deletes all the session data'''
    session.clear()
    flash("You have been successfully logged out", category='success')
    return redirect(url_for('home'))
