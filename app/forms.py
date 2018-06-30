from flask_wtf import Form, FlaskForm
from wtforms import StringField, PasswordField, SelectField, FileField, IntegerField, TextAreaField
from flask_wtf.file import FileRequired
from wtforms.validators import DataRequired, Email, Length, EqualTo
from app import db


class LoginForm(Form):
    login = StringField('login', validators=[DataRequired(), Length(min=5, max=30)])
    password = PasswordField('password', validators=[DataRequired()])

    def validate(self):
        initial_validation = super(LoginForm, self).validate()
        if not initial_validation:
            return False
        cursor = db.cursor()
        cursor.execute("""SELECT user_id FROM dls.logins WHERE login= %s""", [self.login.data])
        id = cursor.fetchone()

        if not id:
            self.login.errors.append("There is no user with this login")
            return False

        cursor.execute("""SELECT password FROM dls.passwords WHERE user_id= %s""", [id])
        password = cursor.fetchone()
        cursor.close()
        if password[0] != str(self.password.data):
            self.password.errors.append("Wrong password")
            return False
        return True


class RegisterForm(Form):
    name = StringField(
        'name',
        validators=[DataRequired()])
    surname = StringField(
        'surname',
        validators=[DataRequired()])
    email = StringField(
        'email',
        validators=[DataRequired(), Email(message=None), Length(min=6, max=255)])
    login = StringField(
        'login',
        validators=[DataRequired(), Length(min=5, max=30)])
    password = PasswordField(
        'password',
        validators=[DataRequired(), Length(min=6, max=255)]
    )
    confirm = PasswordField(
        'Repeat password',
        validators=[
            DataRequired(),
            EqualTo('password', message='Passwords must match.')
        ]
    )

    def validate(self):
        initial_validation = super(RegisterForm, self).validate()
        if not initial_validation:
            return False
        cursor = db.cursor()
        cursor.execute("""SELECT * FROM dls.logins WHERE login= %s""", [self.login.data])
        logins = cursor.fetchone()
        cursor.execute("""SELECT * FROM dls.users WHERE "e-mail"= %s""", [self.email.data])
        emails = cursor.fetchone()
        if logins:
            self.login.errors.append("login already registered")
            return False
        if emails:
            self.email.errors.append("email already registered")
            return False
        return True


class AddCourse(Form):
    course_name = StringField('course', validators=[DataRequired(), Length(max=200)])
    description = TextAreaField('description', validators=[DataRequired(), Length(min=30, max=500)])


class AddUser(Form):
    name = StringField(
        'name',
        validators=[DataRequired()])
    surname = StringField(
        'surname',
        validators=[DataRequired()])
    email = StringField(
        'email',
        validators=[DataRequired(), Email(message=None), Length(min=6, max=255)])
    login = StringField(
        'login',
        validators=[DataRequired(), Length(min=5, max=30)])
    role = SelectField(
        'role',
        coerce=int,
        choices=[(1, 'Студент'), (2, 'Преподаватель'), (3, 'Администратор')]
    )
    password = PasswordField(
        'password',
        validators=[DataRequired(), Length(min=6, max=255)]
    )
    confirm = PasswordField(
        'Repeat password',
        validators=[
            DataRequired(),
            EqualTo('password', message='Passwords must match.')
        ]
    )

    def validate(self):
        initial_validation = super(AddUser, self).validate()
        if not initial_validation:
            return False
        cursor = db.cursor()
        cursor.execute("""SELECT * FROM dls.logins WHERE login= %s""", [self.login.data])
        logins = cursor.fetchone()
        cursor.execute("""SELECT * FROM dls.users WHERE "e-mail"= %s""", [self.email.data])
        emails = cursor.fetchone()
        if logins:
            self.login.errors.append("login already registered")
            return False
        if emails:
            self.email.errors.append("email already registered")
            return False
        return True


class AddTeacher(Form):
    course_name = StringField('course', validators=[DataRequired()])
    teacher = StringField('teacher', validators=[DataRequired()])


class AddMaterial(Form):
    file = FileField(validators=[FileRequired()])


class AddActivity(Form):
    activity_name = StringField(validators=[DataRequired()])
    file = FileField(validators=[FileRequired()])
    cost = IntegerField()

    def validate(self):
        initial_validation = super(AddActivity, self).validate()
        if not initial_validation:
            return False
        if self.cost.data < 0:
            self.cost.errors.append("Incorrect cost")
            return False
        return True


class AddStudentToCourse(Form):
    student = StringField('teacher', validators=[DataRequired()])


class AddMark(Form):
    student = StringField(validators=[DataRequired()])
    mark = IntegerField(validators=[DataRequired()])
    comment = TextAreaField()
