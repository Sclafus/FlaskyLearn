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

    #hashing the sensitive informations
    hhmail = doubleHash(email)
    hhpassword = doubleHash(password)
    hhsurname = doubleHash(surname)

    #add contributor manually
    dbCurr.execute("INSERT INTO Contributor (email, password, name, surname) VALUES (?, ?, ?, ?)",
    (hhmail, hhpassword, name, hhsurname))
    db.commit()
    db.close()
    

if __name__ == '__main__':
    main()