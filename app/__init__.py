import psycopg2
from flask import Flask
from flask_login import LoginManager
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config.from_object('app.config')

lm = LoginManager()
lm.init_app(app)
lm.login_view = 'login'

db = SQLAlchemy(app)
db_ = psycopg2.connect(database="DLS", user="postgres", password="hamster", host="127.0.0.1", port="5432")

migrate = Migrate(app, db)
manager = Manager(app)

manager.add_command('db', MigrateCommand)

from app import views


# q = db.session.query(func.sum(StudentWork.mark), func.sum(Activity.cost), User, Course).join(Activity, StudentWork.activity).join(User, StudentWork.student).join(Course, User.courses).group_by(Course.id, User.id).filter(User.id == 2).all()

