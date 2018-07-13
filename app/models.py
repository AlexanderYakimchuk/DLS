from datetime import datetime

from flask_login import UserMixin

from app import db
from app import db_

user_courses = db.Table('user_courses',
                        db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
                        db.Column('course_id', db.Integer, db.ForeignKey('course.id'), primary_key=True)
                        )


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(50), unique=True, nullable=False)
    login = db.Column(db.String(30), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    name = db.Column(db.String(50), nullable=False)
    surname = db.Column(db.String(50), nullable=False)
    role = db.Column(db.Integer(), nullable=False, default=1)
    courses = db.relationship('Course', secondary=user_courses,
                              backref=db.backref('users'))

    def __repr__(self):
        return self.login


class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    course_name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    materials = db.relationship('Material', backref='course')
    activities = db.relationship('Activity', backref='course')

    def __repr__(self):
        return self.course_name


class File(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    reference = db.Column(db.String, nullable=False)


class Activity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cost = db.Column(db.Float, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    reference = db.Column(db.String, nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)


class Material(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    reference = db.Column(db.String, nullable=False)
    upload_date = db.Column(db.Date, nullable=False, default=datetime.now())
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)


class StudentWork(db.Model):
    activity_id = db.Column(db.Integer, db.ForeignKey('activity.id'), primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)

    name = db.Column(db.String(100), nullable=False)
    reference = db.Column(db.String, nullable=False)
    mark = db.Column(db.Float)
    comment = db.Column(db.String(300))
    upload_date = db.Column(db.DateTime, nullable=False, default=datetime.now())
    evaluation_date = db.Column(db.Date)

    activity = db.relationship('Activity', backref='students')
    student = db.relationship('User', backref='activities')


class User_:
    def __init__(self, name, surname, email, login, password, role=1, id=0):
        self.id = id
        self.email = email
        self.password = password
        self.name = name
        self.surname = surname
        self.login = login
        self.role = role

    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        return self.login

    @staticmethod
    def get_user(login):
        cursor = db_.cursor()
        cursor.execute("""SELECT name, surname, "e-mail", login, password, role, u.user_id
                                        FROM dls.users AS u
                                        JOIN dls.logins AS l
                                        ON u.user_id = l.user_id
                                        JOIN dls.passwords AS p
                                        ON u.user_id = p.user_id
                                        WHERE login = %s""", [login])
        user = cursor.fetchone()
        cursor.close()
        if user:
            return User_(user[0], user[1], user[2], user[3], user[4], user[5], user[6])
        return None

    def insert_into_db(self):
        cursor = db_.cursor()
        cursor.execute("""INSERT INTO dls.users(name, surname, "e-mail", role)
                          VALUES (%s, %s, %s, %s)""", (self.name, self.surname, self.email, self.role))

        cursor.execute("""SELECT MAX(user_id) FROM dls.users""")

        id = cursor.fetchone()
        self.id = id[0]
        cursor.execute("""INSERT INTO dls.logins(user_id, login)
                          VALUES (%s, %s)""", (id, self.login))

        cursor.execute("""INSERT INTO dls.passwords(user_id, password)
                                  VALUES (%s, %s)""", (id, self.password))
        db_.commit()

    def __repr__(self):
        return '<email {}'.format(self.email)


class Course_():
    def __init__(self, course_name, description):
        self.course_name = course_name
        self.description = description

    @staticmethod
    def get_course(name):
        cursor = db_.cursor()
        cursor.execute("""SELECT course_name, description
                        FROM dls.courses
                        WHERE course_name = %s""", [name])
        course = cursor.fetchone()
        cursor.close()
        if course:
            return Course_(course[0], course[1])
        return None
