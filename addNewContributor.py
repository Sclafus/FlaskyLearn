from utils import Utils
from dotenv import load_dotenv
import os

load_dotenv()
env = {
    'dbUser': os.getenv('DB_USER'),
    'dbPassword': os.getenv('DB_PASSWORD'),
    'dbHost': os.getenv('DB_HOST'),
    'dbPort': int(os.getenv('DB_PORT')),
    'dbSchema': os.getenv('DB_SCHEMA'),
    'uploadFolder': os.getenv('UPLOAD_FOLDER'),
    'videoFormats': os.getenv('VIDEO_FORMATS').split(', '),
}

def main():
    #connects to database 
    util = Utils(env)
    db = util.dbConnect()
    dbCurr = db.cursor()

    #gather information from the user
    email = input("Insert the email of the new contributor: ")
    name = input("Insert the name of the new contributor: ")
    surname = input("Insert the surname of the new contributor: ")
    password = input("Insert the password of the new contributor: ")

    #hashing the sensitive informations
    hhmail = util.doubleHash(email)
    hhpassword = util.doubleHash(password)
    hhsurname = util.doubleHash(surname)

    #add contributor manually
    dbCurr.execute("INSERT INTO Contributor (email, password, name, surname) VALUES (?, ?, ?, ?)",
    (hhmail, hhpassword, name, hhsurname))
    db.close()
    

if __name__ == '__main__':
    main()