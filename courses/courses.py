from flask import Blueprint, render_template, request, session, flash, redirect, url_for, make_response
from flaskylearn import db, util, nullTuple
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
    for course in dbCurr:
        courses.append(course)
    dbCurr.close()
    return render_template('courses/courses.html', context=courses)


@courses.route('/<int:courseId>/', methods=['POST', 'GET'])
def specificCourse(courseId: int):
    '''Page for a specified course, dinamically generated'''
    dbCurr = db.cursor()

    # POST request = a user is trying to enroll in the course
    if request.method == 'POST':
        if 'email' in session:
            dbCurr.execute("INSERT INTO Enrollment VALUES (?, ?, ?)",
                           (session['email'], courseId, util.getTimestamp()))
            flash("You have been enrolled successfully", category='success')
        else:
            flash("You need to login in order to enroll in this course!",
                  category='danger')
        dbCurr.close()
        return redirect(request.url)

    # GET request
    videos = []
    # getting course name
    dbCurr.execute("SELECT name FROM Course WHERE id=?", (courseId, ))
    if (courseName := dbCurr.next()) == None:
        flash("The course you are trying to access doesn't exist!", category='danger')
        dbCurr.close()
        return redirect(url_for('courses.homepage'))

    # Getting all the lessons for the specified course
    dbCurr.execute(
        "SELECT videoid, lesson, description FROM Composition INNER JOIN Video ON Video.id = Composition.videoid WHERE Composition.courseid = ? ORDER BY lesson", (courseId,))
    lessons = [lesson for lesson in dbCurr]

    # checking if the lesson has already been viewed
    for videoid, lesson, description in lessons:

        if 'email' in session:
            dbCurr.execute(
                "SELECT EXISTS (SELECT id FROM Visualization WHERE id=? AND email=?)", (videoid, session['email']))
            viewed = True if dbCurr.next() != nullTuple else False
        else:
            viewed = False
        videos.append((lesson, description, viewed if viewed else False))

    # checking if the user is already enrolled
    if 'email' in session:
        dbCurr.execute(
            "SELECT EXISTS (SELECT timestamp FROM Enrollment WHERE email=? AND id=?)", (session['email'], courseId))

        if dbCurr.next() != nullTuple:
            session['enrolled'] = True
    else:
        session['enrolled'] = False
    # checks if the user has seen all the lessons or not
    notViewedVideos = [video for video in videos if not video[2]]
    quizAvailable = True if not notViewedVideos else False
    dbCurr.close()
    return render_template('courses/course.html', courseName=courseName[0], videos=videos, courseId=courseId, quizAvailable=quizAvailable)


@courses.route('/<int:courseId>/lesson<int:lessonId>', methods=['GET', 'POST'])
def specificLesson(courseId: int, lessonId: int):
    '''Page for a specified lesson, displays video'''

    # user is not logged in
    if not 'email' in session:
        flash("You need to login in order to see this lesson", category='warning')
        return redirect(url_for('courses.specificCourse', courseId=courseId))

    if (not session.get('enrolled', default=False) and not 'admin' in session):
        flash("You need to enroll in the course to see the lessons",
              category='warning')
        return redirect(url_for('courses.specificCourse', courseId=courseId))

    dbCurr = db.cursor()
    # POST request
    if request.method == 'POST':

        if 'admin' in session:
            flash("Contributors can't mark videos as played", category='warning')
            dbCurr.close()
            return redirect(request.url)

        # getting back the videoid
        dbCurr.execute(
            "SELECT videoid FROM Composition WHERE courseid=? AND lesson=?", (courseId, lessonId))
        videoId = dbCurr.next()[0]

        # marking the video as played for a student
        ts = util.getTimestamp()
        dbCurr.execute("INSERT INTO Visualization (email, id, timestamp) VALUES (?, ?, ?)",
                       (session['email'], videoId, ts))
        flash("The video has been marked as played", category='success')
        dbCurr.close()
        return redirect(request.url)
    
    # GET request
    if request.method == 'GET':
        # getting course name
        dbCurr.execute("SELECT name FROM Course WHERE id=?", (courseId, ))
        courseName = dbCurr.next()[0]

        # getting video path
        dbCurr.execute(
            "SELECT path FROM Composition INNER JOIN Video on Composition.videoid = Video.id WHERE lesson = ? AND courseid=?", (lessonId, courseId))

        path = dbCurr.next()[0].split('/')
        videoPath = '/'.join(path[-2:])
        folderPath = path[-3]
        dbCurr.close()
        return render_template('courses/lesson.html', courseName=courseName, lessonId=lessonId, videoPath=videoPath, folderPath=folderPath, courseId=courseId)


@lru_cache
@courses.route('/<int:courseId>/quiz', methods=['POST', 'GET'])
def specificQuiz(courseId: int):
    '''Quiz for the specified course'''

    if not 'email' in session:
        # User is not logged in
        flash("You need to login in order to access this page",
              category='warning')
        return redirect(url_for('courses.specificCourse', courseId=courseId))

    dbCurr = db.cursor()
    dbCurr.execute("SELECT EXISTS(SELECT timestamp FROM Enrollment WHERE email=? AND id=?)",
                   (session['email'], courseId))
    authorized = True if dbCurr.next() != nullTuple else False

    if not authorized:
        flash("You need to enroll and watch all the lessons first!",
              category='warning')
        dbCurr.close()
        return redirect(url_for('courses.specificCourse', courseId=courseId))

    # check if user has seen all the lessons
    dbCurr.execute(
        "SELECT COUNT(*) FROM Composition WHERE courseid=?", (courseId,))
    lessonNum = dbCurr.next()[0]

    dbCurr.execute(
        "SELECT COUNT(*) FROM (SELECT DISTINCT * FROM Visualization WHERE email=?) as subquery", (session['email'], ))
    lessonViewed = dbCurr.next()[0]

    if lessonNum > lessonViewed:
        flash("You need to watch all the lessons first!", category='warning')
        dbCurr.close()
        return redirect(url_for('courses.specificCourse', courseId=courseId))

    # Getting the quiz
    quiz = []

    # Getting course name
    dbCurr.execute("SELECT name FROM Course WHERE id=?", (courseId, ))
    courseName = dbCurr.next()[0]

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
            flash(f'Congratulations, you passed the test with a score of {score}, great job! Download your certification with the button below!',
                  category='success')
        else:
            flash(
                f'Your score was {score}, you almost got it! Try again next time', category='danger')
        session['courseName'] = courseName
        session['courseId'] = courseId
        session['score'] = score
        dbCurr.close()
        return redirect(url_for('courses.quizOutcome', courseId=courseId))

    # GET Request
    if request.method == 'GET':
        dbCurr.close()
        if quiz:
            return render_template("courses/quiz.html", courseName=courseName, quiz=quiz)

        flash("The quiz has not been added to this course yet, come back later!",
              category='warning')
        return redirect(url_for('courses.specificCourse', courseId=courseId))


@courses.route('/<int:courseId>/quiz/outcome', methods=['GET', 'POST'])
def quizOutcome(courseId: int):

    if request.method == 'GET':
        if 'score' in session:
            isPassed = True if session['score'] >= 60 else False
            return render_template('courses/quizOutcome.html', isPassed=isPassed, courseId=courseId)
        return render_template('courses/quizOutcome.html', courseId=courseId)

    if request.method == 'POST':
        if 'score' in session:
            # getting course description
            dbCurr = db.cursor()
            dbCurr.execute(
                "SELECT description FROM Course WHERE id=?", (courseId,))

            data = {
                'name': session['name'],
                'surname': session['surname'],
                'course': session['courseName'],
                'timestamp': util.getTimestamp()[:10],
                'description': dbCurr.next()[0]
            }

            pdf = util.generatePDF(render_template(
                'courses/pdfTemplate.html', data=data))

            response = make_response(pdf)
            response.headers['Content-Type'] = 'application/pdf'
            response.headers['Content-Disposition'] = f'inline; filename={data["course"]}_{data["name"]}_{data["surname"]}.pdf'

            # clearing cookie data
            session.pop('courseName')
            session.pop('score')
            dbCurr.close()
            return response
        return redirect(url_for('courses.specificCourse', courseId=courseId))
