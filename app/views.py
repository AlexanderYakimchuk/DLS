from flask import render_template, redirect, request, url_for, sessions, g, flash
from flask_login import login_user, logout_user, current_user, login_required
from app import app, db, lm
from .models import User, Course
from .forms import RegisterForm, LoginForm, AddCourse, AddUser, AddTeacher, \
    AddMaterial, AddActivity, AddStudentToCourse, AddMark
from .db_manager import DBManager
import werkzeug


@app.before_request
def before_request():
    g.user = current_user


@app.route('/')
@app.route('/index', methods=['GET', 'POST'])
def index():
    if g.user is None or not g.user.is_authenticated:
        return redirect('/login')
    if g.user.role == 1:
        return render_template('index.html', user=g.user)
    if g.user.role == 2:
        return render_template('index.html', user=g.user)
    if g.user.role == 3:
        return render_template('admin_index.html', user=g.user)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm(request.form)
    if form.validate_on_submit():
        login_user(User.get_user(form.login.data))
        return redirect('/index')
    return render_template('login.html', form=form)


@app.route('/logout', methods=['GET', 'POST'])
def logout():
    logout_user()
    return redirect('/login')


@app.route('/registration', methods=['GET', 'POST'])
def registration():
    form = RegisterForm(request.form)
    if form.validate_on_submit():
        user = User(
            name=form.name.data,
            surname=form.surname.data,
            email=form.email.data,
            login=form.login.data,
            password=form.password.data
        )
        DBManager.add_user(user)
        login_user(user)
        return redirect("/index")

    return render_template('registration.html', form=form)


@lm.user_loader
def load_user(login):
    return User.get_user(login)


@app.route("/statistic", methods=['GET', 'POST'])
def statistic():
    if g.user is not None and g.user.is_authenticated:
        if g.user.role == 3:
            teacher_popularity = DBManager.get_teacher_popularity()
            courses_statistic = DBManager.get_courses_statistic()
            courses_popularity = DBManager.get_courses_popularity()
            return render_template('admin_statistic.html',
                                   user=g.user,
                                   teacher_popularity=teacher_popularity,
                                   courses_statistic=courses_statistic,
                                   courses_popularity=courses_popularity)

    redirect('/login')


@app.route("/courses", methods=['GET', 'POST'])
def course():
    if g.user and g.user.is_authenticated:
        if g.user.role == 3:
            return render_template("admin_course.html", user=g.user)
        if g.user.role == 2:
            courses = DBManager.get_courses_for_user(g.user.id)
            return render_template("teacher_courses.html", user=g.user, courses=courses)
        if g.user.role == 1:
            courses = DBManager.get_courses_for_user(g.user.id)
            return render_template("teacher_courses.html", user=g.user, courses=courses)
    return redirect("/login")


@app.route("/course/add", methods=['GET', 'POST'])
def course_add():
    if g.user and g.user.is_authenticated:
        if g.user.role == 3:
            form = AddCourse()
            if form.validate_on_submit():
                course = Course(
                    course_name=form.course_name.data,
                    description=form.description.data
                )
                DBManager.add_course(course)
                return redirect("/course/add")
            return render_template('course_form.html', form=form, user=g.user)
    return redirect("/login")


@app.route('/add_user', methods=['GET', 'POST'])
def add_user():
    if g.user and g.user.is_authenticated and g.user.role == 3:
        form = AddUser(request.form)
        if form.validate_on_submit():
            user = User(
                name=form.name.data,
                surname=form.surname.data,
                email=form.email.data,
                login=form.login.data,
                password=form.password.data,
                role=form.role.data
            )
            DBManager.add_user(user)
            return redirect("/add_user")

        return render_template('add_user.html', form=form, user=g.user)


@app.route('/course/add_teacher', methods=['GET', 'POST'])
def add_teacher():
    if g.user and g.user.is_authenticated and g.user.role == 3:
        form = AddTeacher(request.form)
        courses = DBManager.get_courses()
        teachers = DBManager.get_teachers()
        if form.validate_on_submit():
            DBManager.add_user_to_course(form.teacher.data, form.course_name.data, 2)
            return redirect("/course/add_teacher")

        return render_template('add_teacher.html', form=form, user=g.user, courses=courses, teachers=teachers)


@app.route('/courses/<int:course_id>', methods=['GET', 'POST'])
def concrete_course(course_id):
    if g.user is not None and g.user.is_authenticated:
        materials_1 = DBManager.get_materials(course_id, 1)
        activities = DBManager.get_activities(course_id)
        add_material_form = AddMaterial()
        add_lab_form = AddActivity()
        if g.user.role == 1:
            return render_template('course.html', user=g.user,
                                   materials_1=materials_1,
                                   activities=activities,
                                   course_id=str(course_id))
        if g.user.role == 2:
            students_in_course = DBManager.get_students_in_course(course_id)
            return render_template('course.html', user=g.user,
                                   materials_1=materials_1,
                                   activities=activities,
                                   students_in_course=students_in_course,
                                   course_id=str(course_id)
                                   )
    return redirect("/login")


@app.route('/add_material/<int:course_id>', methods=['GET', 'POST'])
def add_material(course_id):
    if g.user is not None and g.user.is_authenticated:
        materials_1 = DBManager.get_materials(course_id, 1)
        activities = DBManager.get_activities(course_id)
        students_in_course = DBManager.get_students_in_course(course_id)
        add_material_form = AddMaterial()
        if add_material_form.validate_on_submit():
            filename = add_material_form.file.data.filename
            material_id = DBManager.add_material(filename, course_id)
            add_material_form.file.data.save('app/static/files/' + str(material_id) + filename)
            return redirect('/courses/' + str(course_id))
        return render_template("add_material_form.html",
                               user=g.user,
                               materials_1=materials_1,
                               activities=activities,
                               students_in_course=students_in_course,
                               course_id=str(course_id),
                               add_material_form=add_material_form)
    return redirect("/login")


@app.route('/add_lab/<int:course_id>', methods=['GET', 'POST'])
def add_lab(course_id):
    if g.user is not None and g.user.is_authenticated:
        materials_1 = DBManager.get_materials(course_id, 1)
        activities = DBManager.get_activities(course_id)
        students_in_course = DBManager.get_students_in_course(course_id)
        add_lab_form = AddActivity()
        if add_lab_form.validate_on_submit():
            filename = add_lab_form.file.data.filename
            cost = add_lab_form.cost.data
            name = add_lab_form.activity_name.data
            material_id = DBManager.add_activity(filename, course_id, name, cost)
            add_lab_form.file.data.save('app/static/files/' + str(material_id) + filename)

            return redirect('/courses/' + str(course_id))
        return render_template("add_lab_form.html",
                               user=g.user,
                               materials_1=materials_1,
                               activities=activities,
                               students_in_course=students_in_course,
                               course_id=str(course_id),
                               add_lab_form=add_lab_form
                               )
    return redirect("/login")


@app.route('/add_student/<int:course_id>', methods=['GET', 'POST'])
def add_student(course_id):
    if g.user is not None and g.user.is_authenticated:
        materials_1 = DBManager.get_materials(course_id, 1)
        activities = DBManager.get_activities(course_id)
        students_in_course = DBManager.get_students_in_course(course_id)
        all_students = DBManager.get_students()
        add_student_form = AddStudentToCourse()

        if add_student_form.validate_on_submit():
            DBManager.add_user_to_course(add_student_form.student.data, course_id, 1)
            return redirect('/courses/' + str(course_id))
        return render_template("add_student.html",
                               user=g.user,
                               materials_1=materials_1,
                               activities=activities,
                               students_in_course=students_in_course,
                               all_students=all_students,
                               course_id=str(course_id),
                               add_student_form=add_student_form)
    return redirect("/login")


@app.route('/activity/<int:activity_id>', methods=['GET', 'POST'])
def activity(activity_id):
    if g.user is not None and g.user.is_authenticated:
        activity = DBManager.get_activity(activity_id)
        add_material_form = AddMaterial()
        student_activity = DBManager.get_activity_for_student(g.user.id, activity_id)
        if add_material_form.validate_on_submit():
            filename = add_material_form.file.data.filename
            DBManager.add_student_to_activity(g.user.id, activity_id, filename)
            add_material_form.file.data.save('app/static/files/' + str(g.user.id) + str(activity_id) + filename)
        return render_template('activity.html',
                               user=g.user,
                               activity_id=str(activity_id),
                               user_id=str(g.user.id),
                               activity=activity,
                               student_activity=student_activity,
                               add_material_form=add_material_form
                               )
    return redirect("/login")


@app.route('/t_activity/<int:course_id>/<int:activity_id>', methods=['GET', 'POST'])
def t_activity(course_id, activity_id):
    if g.user is not None and g.user.is_authenticated:
        activity = DBManager.get_activity(activity_id)
        students = DBManager.get_students_activities(course_id, activity_id)
        add_mark_form = AddMark()
        if add_mark_form.validate_on_submit():
            name = add_mark_form.student.data
            student_id = None
            for student in students:
                if name == student[0] + ' ' + student[1]:
                    student_id = int(student[5])
            DBManager.add_mark(student_id, activity_id, add_mark_form.mark.data, add_mark_form.comment.data)
            return redirect('/t_activity/' + str(course_id) + '/' + str(activity_id))
        return render_template('t_activity.html',
                               user=g.user,
                               activity_id=str(activity_id),
                               user_id=str(g.user.id),
                               activity=activity,
                               students=students,
                               course_id=str(course_id),
                               add_mark_form=add_mark_form
                               )
    return redirect("/login")


@app.route('/courses/<int:course_id>/result', methods=['GET', 'POST'])
def concrete_course_result(course_id):
    if g.user is not None and g.user.is_authenticated:

        if g.user.role == 1:
            result = DBManager().get_course_result_for_student(course_id, g.user.id)
            return render_template('s_course_result.html', user=g.user,
                                   course_id=str(course_id),
                                   result=result
                                   )
        if g.user.role == 2:
            course_result = DBManager.get_course_result(course_id)
            productivity = DBManager.get_course_productivity(course_id)
            return render_template('t_course_result.html', user=g.user,
                                   course_id=str(course_id),
                                   result=course_result,
                                   productivity=productivity
                                   )
    return redirect("/login")


@app.route('/my_progress', methods=['GET', 'POST'])
def progress():
    if g.user is not None and g.user.is_authenticated:
        my_statistic = DBManager.get_courses_statistic_for_student(g.user.id)
        return render_template('my_progress.html',
                               user=g.user,
                               statistic=my_statistic)

    return redirect("/login")
