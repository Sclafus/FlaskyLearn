import mariadb
from Crypto.Hash import SHA3_256
from datetime import datetime
import pdfkit
from math import trunc
from flask import abort, flash, session


class Utils:

    def __init__(self, env: dict):
        self._env = env

    def doubleHash(self, toBeHashed: str) -> str:
        '''Return the double hash of the input string'''
        return SHA3_256.new((SHA3_256.new(toBeHashed.encode()).hexdigest()).encode()).hexdigest()

    def allowedFile(self, filename: str) -> bool:
        '''Checks if the file is currently being accepted to upload'''

        ext = filename.split(".")[-1]
        if ext in self._env['videoFormats']:
            return True
        return False

    def dbConnect(self):
        '''Returns connection to the local database object'''

        try:
            conn = mariadb.connect(
                user=self._env['dbUser'],
                password=self._env['dbPassword'],
                host=self._env['dbHost'],
                port=self._env['dbPort'],
                database=self._env['dbSchema'],
                autocommit=True
            )
            return conn

        except mariadb.Error as e:
            print(f"Error connecting to MariaDB Platform: {e}")
            raise Exception
        return None

    def getTimestamp(self):
        '''Returns the timestamp right now'''
        return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    def getEnv(self) -> dict:
        '''Returns the env'''
        return self._env

    def generatePDF(self, htmlTemplate: str):
        '''generates PDF for the specified name and course'''
        css = 'flaskylearn/static/css/pdfTemplateStyle.css'
        options = {
            'quiet': '',
            'orientation': 'landscape'
        }
        return pdfkit.from_string(htmlTemplate, False, options=options, css=css)

    def quizChecker(self, quiz: list, responses: dict, threshold: int) -> (int, bool):
        '''checks if the specified quiz and the given responses meet the threshold'''
        # Calculating the points per question
        pointPerQuestion = 100 / len(quiz)
        points = 0

        for questionIndex, question in enumerate(quiz, start=1):
            wrongAnswers = 0
            rightAnswers = 0
            answers = question['answers']
            for key in responses:
                if key[-3] == str(questionIndex):
                    answer = responses[key]
                    isCorrect = answers[int(key[-1])-1]['answerCorrect']

                    if answer == isCorrect:
                        rightAnswers += 1
                    else:
                        wrongAnswers += 1
            try:
                points += (rightAnswers * pointPerQuestion) / \
                    (rightAnswers + wrongAnswers)
            except ZeroDivisionError:
                # no answer given
                pass

        if points >= threshold:
            return trunc(points), True
        return trunc(points), False

    def requireAdminLogin(self):
        ''' Checks if the user has the sufficient permission to view the page'''
        dbCurr = self.dbConnect().cursor()

        # permission check
        if 'email' in session:
            dbCurr.execute('SELECT EXISTS(SELECT email FROM Contributor WHERE email=? AND password=?)',
                           (session['email'], session['password']))
        authorized = True if dbCurr.next() != (0,) else False

        if ((not authorized) or ('email' not in session)):
            flash("Nice try.", category="danger")
            return abort(403)
        return
