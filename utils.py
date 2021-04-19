
from Crypto.Hash import SHA3_256

class Utils:

    def __init__(self, _env: dict):
        self.env = _env


    def doubleHash(self, toBeHashed: str) -> str:
        '''
        return the double hash of the input string
        '''
        return SHA3_256.new((SHA3_256.new(toBeHashed.encode()).hexdigest()).encode()).hexdigest()


    def allowedFile(self, filename: str) -> bool:
        '''
        Checks if the file is currently being accepted to upload
        '''
        ext = filename.split(".")[-1]
        if ext in self.env['videoFormats']:
            return True
        return False