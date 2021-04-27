[![CodeFactor](https://www.codefactor.io/repository/github/sclafus/flaskylearn/badge?s=28707972a0d84d5d62a586329595199834fb0240)](https://www.codefactor.io/repository/github/sclafus/flaskylearn)
# FlaskyLearn

FlaskyLearn is a web application built with Python 3 and Flask. 
The main purpose of this application is offering a free, easy to use and simple to deploy 
web app for all the non technical people around the world.

### .env file format

```.env
SECRET_KEY="development"

# Database stuff
DB_USER="root"
DB_PASSWORD="admin"
DB_HOST="localhost"
DB_PORT=3306
DB_SCHEMA="flaskylearn"

#File stuff
UPLOAD_FOLDER="./static/videos"
VIDEO_FORMATS = "webm, mkv, flv, avi, mov, wmv, mp4, m4v, 3gp"
```

# Installation
Dependencies:
- MariaDB
- Python (3.9 is recommended)

## Deployment with Docker
TODO

## Standard Deployment
1. Install MariaDB and Python using your package manager.

    - For Debian/Ubuntu based distros using `apt`

      `sudo apt install -y mariadb-server python` //FIX 

    - For Arch based distros using `pacman`

      `sudo pacman -S mariadb python`

    - For REHL/CentOS/Oracle Linux using `yum`

      `sudo yum install -y mariadb python` //FIX

2. Clone the repository

    `git clone https://github.com/Sclafus/FlaskyLearn.git`

3. Create a new user for your database using a strong password

4. Create the database using the createDB.sql file

5. Enable `mariadb.service` on startup with `systemd`

6. Add a new Contributor using `addNewContributor.py`

7. Start the Flask app and make sure everything is working

8. Enable on startup