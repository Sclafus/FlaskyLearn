from flask import Blueprint, render_template, request, session, flash, redirect, url_for, make_response
from flaskylearn import db, util
from datetime import datetime
from functools import lru_cache
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


@courses.route('/<int:courseId>/', methods=['POST', 'GET'])
def specificCourse(courseId: int):
    '''Page for a specified course, dinamically generated'''
    dbCurr = db.cursor()

    # POST request = a user is trying to enroll in the course
    if request.method == 'POST':
        dbCurr.execute("INSERT INTO Enrollment VALUES (?, ?, ?)",
                       (session['email'], courseId, util.getTimestamp()))
        flash("You have been enrolled successfully", category='success')
        return redirect(request.url)

    # GET request
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

    # checking if the lesson has already been viewed
    for lesson, description in lessons:
        flag = False

        try:
            dbCurr.execute(
                "SELECT id FROM Visualization WHERE id=? AND email=?", (lesson, session['email']))
            for _ in dbCurr:
                flag = True
        except KeyError:
            # user not logged in
            pass

        videos.append((lesson, description, flag))

    # checking if the user is already enrolled
    session['enrolled'] = False
    try:
        dbCurr.execute(
            "SELECT timestamp FROM Enrollment WHERE email=? AND id=?", (session['email'], courseId))

        for _ in dbCurr:
            session['enrolled'] = True

    except KeyError:
        # user not logged in, enrollment is not applicable
        pass

    # checks if the user has seen all the lessons or not
    notViewedVideos = [video for video in videos if not video[2]]
    quizAvailable = True if not notViewedVideos else False
    return render_template('courses/course.html', courseName=courseName, videos=videos, courseId=courseId, quizAvailable=quizAvailable)


@courses.route('/<int:courseId>/lesson<int:lessonId>', methods=['GET', 'POST'])
def specificLesson(courseId: int, lessonId: int):
    '''Page for a specified lesson, displays video'''
    dbCurr = db.cursor()

    # user is not logged in
    if not 'email' in session:
        flash("You need to login in order to see this lesson", category='warning')
        return redirect(url_for('courses.specificCourse', courseId=courseId))

    try:
        if (not session['enrolled'] and not 'admin' in session):
            flash("You need to enroll in the course to see the lessons",
                  category='warning')
            return redirect(url_for('courses.specificCourse', courseId=courseId))
    except KeyError:
        return redirect(url_for('courses.specificCourse', courseId=courseId))

    # POST Request
    if request.method == 'POST':

        if 'admin' in session:
            flash("Contributors can't mark videos as played", category='warning')
            return redirect(request.url)

        # getting back the videoid
        dbCurr.execute(
            "SELECT videoid FROM Composition WHERE courseid=? AND lesson=?", (courseId, lessonId))
        for _videoid in dbCurr:
            videoId = _videoid[0]

        # marking the video as played for a student
        ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        dbCurr.execute("INSERT INTO Visualization (email, id, timestamp) VALUES (?, ?, ?)",
                       (session['email'], videoId, ts))
        flash("The video has been marked as played", category='success')
        return redirect(request.url)

    # GET Request
    # getting course name
    dbCurr.execute("SELECT name FROM Course WHERE id=?", (courseId, ))
    for _courseName in dbCurr:
        courseName = _courseName[0]

    # getting video path
    dbCurr.execute(
        "SELECT path FROM Composition INNER JOIN Video on Composition.videoid = Video.id WHERE lesson = ? AND courseid=?", (lessonId, courseId))

    for _path in dbCurr:
        path = _path[0].split('/')
        videoPath = '/'.join(path[-2:])
        folderPath = path[-3]

    return render_template('courses/lesson.html', courseName=courseName, lessonId=lessonId, videoPath=videoPath, folderPath=folderPath, courseId=courseId)


@lru_cache
@courses.route('/<int:courseId>/quiz', methods=['POST', 'GET'])
def specificQuiz(courseId: int):
    '''Quiz for the specified course'''
    dbCurr = db.cursor()

    # User permission check
    authorized = False
    try:
        dbCurr.execute(
            "SELECT timestamp FROM Enrollment WHERE email=? AND id=?", (session['email'], courseId))
        for _ in dbCurr:
            authorized = True
    except KeyError:
        # User is not logged in
        pass

    if not authorized:
        if 'email' not in session:
            flash("You need to login in order to access this page",
                  category='warning')
        else:
            flash("You need to watch all the videos first!", category='warning')
        return redirect(url_for('courses.specificCourse', courseId=courseId))

    # Getting the quiz
    quiz = []

    # Getting course name
    dbCurr.execute("SELECT name FROM Course WHERE id=?", (courseId, ))
    for _courseName in dbCurr:
        courseName = _courseName[0]

    # getting questions id for the test
    dbCurr.execute(
        "SELECT questionid, topic FROM Test INNER JOIN Question ON Test.questionid = Question.id WHERE courseid=?", (courseId,))
    for questionId, questionText in dbCurr:
        question = {"questionText": questionText,
                    "questionId": questionId, "answers": []}
        quiz.append(question)

    for _question in quiz:
        dbCurr.execute(
            "SELECT topic, correct FROM Answer INNER JOIN MadeUp ON Answer.id = MadeUp.answerid WHERE questionid=?", (_question['questionId'], ))
        for topic, correct in dbCurr:
            _question['answers'].append(
                {"answerText": topic, "answerCorrect": True if correct else False})

    # POST Request
    if request.method == 'POST':

        # converting 'on' and 'off' values to boolean
        answers = request.form.to_dict()
        for key, value in answers.items():
            answers[key] = True if value == 'on' else False

        score, testPassed = util.quizChecker(quiz, answers, 60)
        if testPassed:
            flash(f'Congratulations, you passed the test with a score of {score}! Download the certificate with the button below!',
                  category='success')
        else:
            flash(
                f'Your score was {score}, you almost got it! Try again next time', category='danger')
        session['courseName'] = courseName
        session['score'] = score
        return redirect(url_for('courses.quizOutcome', courseId=courseId))

    # GET Request
    if request.method == 'GET':
        if quiz:
            return render_template("courses/quiz.html", courseName=courseName, quiz=quiz)
        flash("The quiz has not been added to this course yet, come back later!",
              category='warning')
        return redirect(url_for('courses.specificCourse', courseId=courseId))


@courses.route('/<int:courseId>/quiz/outcome', methods=['GET', 'POST'])
def quizOutcome(courseId: int):

    if request.method == 'GET':
        try:
            isPassed = True if session['score'] >= 60 else False
            return render_template('courses/quizOutcome.html', isPassed=isPassed, courseId=courseId)
        except KeyError:
            return render_template('courses/quizOutcome.html', courseId=courseId)
    if request.method == 'POST':
        try:
            pdf = util.generatePDF(render_template(
                'courses/pdfTemplate.html', name=session['name'], surname=session['surname'], course=session['courseName'], ))

            response = make_response(pdf)
            response.headers['Content-Type'] = 'application/pdf'
            response.headers['Content-Disposition'] = f'inline; filename={session["courseName"]}_{session["name"]}_{session["surname"]}.pdf'

            # clearing cookie data
            session.pop('courseName')
            session.pop('score')
            return response
        except KeyError:
            return redirect(url_for('courses.specificCourse', courseId=courseId))
