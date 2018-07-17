from flask_wtf import Form, FlaskForm
from flask_wtf.file import FileRequired
from wtforms import StringField, PasswordField, SelectField, FileField, IntegerField, TextAreaField
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from wtforms.validators import DataRequired, Email, Length, EqualTo

from app.models import User, get_teachers, get_courses


class LoginForm(FlaskForm):
    login = StringField('login', validators=[DataRequired(), Length(min=5, max=50)])
    password = PasswordField('password', validators=[DataRequired(), Length(min=6, max=30)])


class SignupForm(FlaskForm):
    name = StringField('name', validators=[DataRequired(), Length(max=50)])
    surname = StringField('surname', validators=[DataRequired(), Length(max=50)])
    email = StringField('email', validators=[DataRequired(), Email(message="bad e-mail")])
    login = StringField('login', validators=[DataRequired(), Length(min=5, max=30)])
    password = PasswordField('password', validators=[DataRequired(), Length(min=6, max=20)])
    confirm = PasswordField('confirm', validators=[DataRequired(), Length(min=6, max=20)])

    def validate(self):
        initial_validation = super(SignupForm, self).validate()
        if not initial_validation:
            return False
        if self.password.data != self.confirm.data:
            self.confirm.errors.append("Confirm must be the same")
            return False
        if User.query.filter_by(login=str(self.login)).first():
            self.login.errors.append("User with the same login is already exist")
            return False
        if User.query.filter_by(email=str(self.email)).first():
            self.email.errors.append("You already have account with this email")
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
        login = User.query.filter_by(login=str(self.login)).first()
        email = User.query.filter_by(email=str(self.email)).first()
        if login:
            self.login.errors.append("login already registered")
            return False
        if email:
            self.email.errors.append("email already registered")
            return False
        return True


class AddTeacher(Form):
    course = QuerySelectField('course', query_factory=get_courses, get_label='course_name', allow_blank=False)
    teacher = QuerySelectField('teacher', query_factory=get_teachers, allow_blank=False)


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
    student = QuerySelectField('student', allow_blank=False)


class AddMark(Form):
    student = QuerySelectField('student')
    mark = IntegerField(validators=[DataRequired()])
    comment = TextAreaField()
