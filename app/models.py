import datetime
from app import db


class User:
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
        cursor = db.cursor()
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
            return User(user[0], user[1], user[2], user[3], user[4], user[5], user[6])
        return None

    def insert_into_db(self):
        cursor = db.cursor()
        cursor.execute("""INSERT INTO dls.users(name, surname, "e-mail", role)
                          VALUES (%s, %s, %s, %s)""", (self.name, self.surname, self.email, self.role))

        cursor.execute("""SELECT MAX(user_id) FROM dls.users""")

        id = cursor.fetchone()
        self.id = id[0]
        cursor.execute("""INSERT INTO dls.logins(user_id, login)
                          VALUES (%s, %s)""", (id, self.login))

        cursor.execute("""INSERT INTO dls.passwords(user_id, password)
                                  VALUES (%s, %s)""", (id, self.password))
        db.commit()

    def __repr__(self):
        return '<email {}'.format(self.email)


class Course():
    def __init__(self, course_name, description):
        self.course_name = course_name
        self.description = description

    @staticmethod
    def get_course(name):
        cursor = db.cursor()
        cursor.execute("""SELECT course_name, description
                        FROM dls.courses
                        WHERE course_name = %s""", [name])
        course = cursor.fetchone()
        cursor.close()
        if course:
            return Course(course[0], course[1])
        return None
