from flask import Flask, logging
from dotenv import load_dotenv

import inspect
import dropbox
import os

load_dotenv()

app = Flask(__name__)

# Set up the application configuration
app.config["ENV"] = os.environ.get("FLASK_ENV")
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
    "DATABASE_URI", default="postgresql://localhost/endurance"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = os.environ.get(
    "SECRET_KEY", default="You need a secret, shh, don't tell anyone!"
)
app.config["WTF_CSRF_TIME_LIMIT"] = None
app.config["MAIL_SERVER"] = os.environ.get("MAIL_SERVER")
app.config["MAIL_PORT"] = os.environ.get("MAIL_PORT")
app.config["MAIL_USE_TLS"] = False
app.config["MAIL_USE_SSL"] = os.environ.get("MAIL_USE_SSL")
app.config["MAIL_USERNAME"] = os.environ.get("MAIL_USERNAME")
app.config["MAIL_PASSWORD"] = os.environ.get("MAIL_PASSWORD")

# set up redis queue
from rq import Queue
import redis

r = redis.Redis()
q = Queue(connection=r, default_timeout=120)

# set up CSRF
from flask_wtf.csrf import CSRFProtect

csrf = CSRFProtect(app)

# set up login
from flask_login import LoginManager

login_manager = LoginManager(app=app)
login_manager.init_app(app=app)

# set up database
from web.models import db
from web.models import Member, Major, Minor

db.app = app
db.init_app(app)

# set up dropbox
from dropbox import Dropbox

dropbox_token = os.environ.get("DROPBOX_API_KEY")

if dropbox_token is None:
    app.logger.error(
        "Environment variable DROPBOX_API_KEY required for Dropbox functionality."
    )

dbx = Dropbox(dropbox_token)

# set up mail
from flask_mail import Mail

mail = Mail()
mail.init_app(app)


# import controllers and register the templates
import web.controllers

# Adding CLI commands below... TODO move this to another file, for
#   some reason flask_script wasn't working
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


@app.cli.command("setup-db")
def setup_db():
    """Create database and import Majors/Minors"""
    print("Clearing any pending session actions")
    db.session.remove()
    print("Dropping Tables")
    db.drop_all()
    print("Creating Tables")
    db.create_all()
    print("Committing")
    db.session.commit()
    print("Done!")


@app.cli.command("import-member")
def import_member():
    from web.dropbox import dropbox_setup_member

    member = Member(
        email="dangonzo@mit.edu",
        first_name="Daniel",
        initials="G.",
        last_name="Gonzalez Cunningham",
        class_year=2020,
    )

    major_1 = Major.query.filter_by(
        name="Electrical Engineering and Computer Science"
    ).first()
    major_2 = Major.query.filter_by(
        name="Earth, Atmospheric, and Planetary Sciences"
    ).first()
    member.major.extend([major_1, major_2])

    minor_1 = Minor.query.filter_by(name="Finance").first()
    minor_2 = Minor.query.filter_by(name="French").first()
    minor_3 = Minor.query.filter_by(name="German").first()
    minor_4 = Minor.query.filter_by(name="History").first()
    member.minor.extend([minor_1, minor_2, minor_3, minor_4])

    dropbox_setup_member(member)

    db.session.add(member)
    db.session.commit()


@app.cli.command("get-member")
def get_member():
    member = Member.query.filter_by(email="dangonzo@mit.edu").first()
    print(f"Name: {member.first_name} {member.initials} {member.last_name}")
    print("Year: ", member.class_year)
    print("Major(s): ", member.major)
    print("Minor(s): ", member.minor)
    print("Dropbox Link: ", member.dropbox_file_upload_url)


@app.cli.command("get-major")
def get_major():
    major = Major.query.filter_by(
        name="Electrical Engineering and Computer Science"
    ).first()

    print(major.victims)


@app.cli.command("import-studies")
def import_studies():
    """Do things"""

    print("Adding Majors")
    with open(file="majors.txt", mode="r") as majors:
        for major in majors:
            shorthand, name = major.split(",", 1)
            name = name.replace("\n", "")
            name = name.replace('"', "")

            major_object = Major(shorthand=shorthand, name=name)

            db.session.add(major_object)

    print("Adding Minors")
    with open(file="minors.txt", mode="r") as minors:
        for minor in minors:
            shorthand, name = minor.split(",", 1)
            name = name.replace("\n", "")
            name = name.replace('"', "")

            minor_object = Minor(shorthand=shorthand, name=name)

            db.session.add(minor_object)

    print("Committing Changes")
    db.session.commit()
