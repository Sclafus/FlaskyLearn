import mariadb
from Crypto.Hash import SHA3_256

class Utils:

    def __init__(self, env: dict):
        self._env = env


    def doubleHash(self, toBeHashed: str) -> str:
        '''
        return the double hash of the input string
        '''
        return SHA3_256.new((SHA3_256.new(toBeHashed.encode()).hexdigest()).encode()).hexdigest()


    def allowedFile(self, filename: str) -> bool:
        '''Checks if the file is currently being accepted to upload'''

        ext = filename.split(".")[-1]
        if ext in self.env['videoFormats']:
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