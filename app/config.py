import os

basedir = os.path.abspath(os.path.dirname(__file__))

WTF_CSRF_ENABLED = True
SECRET_KEY = 'you-will-never-guess'
SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:hamster@localhost:5432/DLS'
SQLALCHEMY_TRACK_MODIFICATIONS = False
UPLOAD_FOLDER = 'app/static'
