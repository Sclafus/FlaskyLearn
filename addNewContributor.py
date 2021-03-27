from server import dbConnect, doubleHash


def main():
    #connects to database 
    db = dbConnect()
    dbCurr = db.cursor()

    #gather information from the user
    email = input("Insert the email of the new contributor: ")
    name = input("Insert the name of the new contributor: ")
    surname = input("Insert the surname of the new contributor: ")
    password = input("Insert the password of the new contributor: ")
    
    #add contributor manually
    dbCurr.execute("INSERT INTO Contributor (email, password, name, surname) VALUES (?, ?, ?, ?)",
    (doubleHash(email), doubleHash(password), name, doubleHash(surname)))
    db.commit()
    db.close()
    

if __name__ == '__main__':
    main()