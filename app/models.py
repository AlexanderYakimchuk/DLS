from datetime import datetime

from flask_login import UserMixin
from sqlalchemy import func

from app import db

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
    courses = db.relationship('Course',
                              secondary=user_courses,
                              backref='users')

    def __repr__(self):
        return self.name + ' ' + self.surname





class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    course_name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    materials = db.relationship('Material', backref='course')
    activities = db.relationship('Activity', backref='course')

    students = db.relationship('User',
                               secondary=user_courses,
                               secondaryjoin='and_(User.id == user_courses.c.user_id, User.role == 1)')
    teachers = db.relationship('User',
                               secondary=user_courses,
                               secondaryjoin='and_(User.id == user_courses.c.user_id, User.role == 2)')

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
    added_date = db.Column(db.Date, default=datetime.now())
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


def get_teachers():
    return User.query.filter_by(role=2).order_by(User.surname, User.name)


def get_courses():
    return Course.query.order_by(Course.course_name)


def get_all_students(course_id):
    """
    return all students except students in course with id == course_id

    """
    return lambda: User.query.filter(~User.courses.any(Course.id == course_id), User.role == 1).order_by(User.surname,
                                                                                                         User.name)


def get_students_in_course(course_id):
    return lambda: User.query.filter(User.courses.any(Course.id == course_id), User.role == 1).order_by(User.surname,
                                                                                                        User.name)


def get_student_results(student_id):
    query_result = db.session.query(func.sum(StudentWork.mark), func.sum(Activity.cost), Course.course_name
                                    ).join(Activity, StudentWork.activity
                                           ).join(User, StudentWork.student
                                                  ).join(Course, User.courses
                                                         ).group_by(Course.id, User.id
                                                                    ).filter(User.id == student_id
                                                                             ).all()
    query_labels = ['student_rating', 'max_rating', 'course']
    return list(map(lambda x: dict(zip(query_labels, x)), query_result))


def get_student_result_in_course(student_id, course_id):
    query_result = db.session.query(StudentWork.mark, Activity.cost, Activity.name
                                    ).join(Activity, StudentWork.activity
                                           ).filter(StudentWork.student_id == student_id,
                                                    Activity.course_id == course_id
                                                    ).all()
    query_labels = ['mark', 'cost', 'activity_name']
    return list(map(lambda x: dict(zip(query_labels, x)), query_result))


def get_reasonable_mark(percent):
    if percent >= 95:
        mark = 'A'
    elif percent >= 85:
        mark = 'B'
    elif percent >= 75:
        mark = 'C'
    elif percent >= 65:
        mark = 'D'
    elif percent >= 60:
        mark = 'E'
    else:
        mark = 'F'

    return mark


def get_course_result(course_id):
    query_result = db.session.query(func.sum(StudentWork.mark), func.sum(Activity.cost), User.name, User.surname,
                                    Course.course_name
                                    ).join(Activity, StudentWork.activity
                                           ).join(User, StudentWork.student
                                                  ).join(Course, User.courses
                                                         ).group_by(Course.id, User.id
                                                                    ).filter(Course.id == course_id
                                                                             ).all()
    query_labels = ['student_rating', 'max_rating', 's_name', 's_surname', 'course', 'percent', 'r_mark']
    return list(
        map(
            lambda x: dict(
                zip(
                    query_labels,
                    x + (int(x[0] * 1000 / x[1]) / 10, get_reasonable_mark(x[0] * 1000 / x[1])))
            ),
            query_result)
    )