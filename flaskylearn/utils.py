import mariadb
from Crypto.Hash import SHA3_256
from datetime import datetime
import pdfkit


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
        return pdfkit.from_string(htmlTemplate, False)

    def quizChecker(self, quiz: list, responses: dict, threshold: int) -> bool:
        '''checks if the specified quiz and the given responses meet the threshold'''
        # TODO calculate the minimum amount of questions to pass
        # this method will be quite complex, i need time
        questionNum = len(quiz)
        questionIndex = 1
        for question in quiz:
            answers = question['answers']
            for key in responses:
                if key[7] == str(questionIndex):
                    # to implement
                    print('hi')
            questionIndex += 1
        return True
