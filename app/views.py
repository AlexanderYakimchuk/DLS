import os

from flask import render_template, redirect, request
from flask_login import logout_user, login_user, current_user, login_required
from werkzeug.security import check_password_hash, generate_password_hash

from app import app, lm
from app import db
from .forms import SignupForm, LoginForm, AddCourse, AddUser, AddTeacher, \
    AddMaterial, AddActivity, AddStudentToCourse, AddMark
from .models import User, Course, Activity, StudentWork, Material, get_all_students, get_students_in_course, \
    get_student_results


@lm.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/')
@app.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    if current_user.role == 1:
        return render_template('index.html', user=current_user)
    if current_user.role == 2:
        return render_template('index.html', user=current_user)
    if current_user.role == 3:
        return render_template('admin_index.html', user=current_user)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm(request.form)
    if form.validate_on_submit():
        user = User.query.filter_by(login=form.login.data).first()
        if check_password_hash(user.password, form.password.data):
            login_user(user)
            return redirect('/')
    return render_template("login.html",
                           form=form)


@app.route('/logout', methods=['GET', 'POST'])
def logout():
    logout_user()
    return redirect('/login')


@app.route('/signup', methods=["GET", "POST"])
def signup():
    form = SignupForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(password=form.password.data, method="sha256")
        new_user = User(
            name=form.name.data,
            surname=form.surname.data,
            email=form.email.data,
            login=form.login.data,
            password=hashed_password
        )
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        return redirect("/")
    return render_template("signup.html",
                           form=form)


# @app.route("/statistic", methods=['GET', 'POST'])
# def statistic():
#     if g.user is not None and g.user.is_authenticated:
#         if g.user.role == 3:
#             teacher_popularity = DBManager.get_teacher_popularity()
#             courses_statistic = DBManager.get_courses_statistic()
#             courses_popularity = DBManager.get_courses_popularity()
#             return render_template('admin_statistic.html',
#                                    user=g.user,
#                                    teacher_popularity=teacher_popularity,
#                                    courses_statistic=courses_statistic,
#                                    courses_popularity=courses_popularity)
#
#     redirect('/login')


@app.route("/courses", methods=['GET', 'POST'])
@login_required
def course():
    if current_user.role == 3:
        return render_template("admin_course.html", user=current_user)

    return render_template("course_list.html",
                           user=current_user,
                           courses=current_user.courses)


@app.route("/course/add", methods=['GET', 'POST'])
@login_required
def course_add():
    if current_user.role == 3:
        form = AddCourse()
        if form.validate_on_submit():
            course = Course(
                course_name=form.course_name.data,
                description=form.description.data
            )
            db.session.add(course)
            db.session.commit()
            return redirect("/course/add")
        return render_template('course_form.html', form=form, user=current_user)


@app.route('/add_user', methods=['GET', 'POST'])
@login_required
def add_user():
    if current_user.role == 3:
        form = AddUser(request.form)
        if form.validate_on_submit():
            user = User(
                name=form.name.data,
                surname=form.surname.data,
                email=form.email.data,
                login=form.login.data,
                password=generate_password_hash(form.password.data, 'sha256'),
                role=form.role.data
            )
            db.session.add(user)
            db.session.commit()
            return redirect("/add_user")

        return render_template('add_user.html', form=form, user=current_user)


@app.route('/course/add_teacher', methods=['GET', 'POST'])
@login_required
def add_teacher():
    if current_user.role == 3:
        form = AddTeacher(request.form)
        courses = Course.query.all()
        teachers = User.query.filter_by(role=2)
        form.teacher_list = teachers
        if form.validate_on_submit():
            teacher = form.teacher.data
            teacher.courses.append(form.course.data)
            db.session.commit()
            return redirect("/course/add_teacher")

        return render_template('add_teacher.html', form=form, user=current_user, courses=courses, teachers=teachers)


@app.route('/courses/<int:course_id>', methods=['GET', 'POST'])
def concrete_course(course_id):
    if current_user.role == 1:
        return render_template('course.html', user=current_user,
                               course=Course.query.get(course_id))
    if current_user.role == 2:
        return render_template('course.html',
                               user=current_user,
                               course=Course.query.get(course_id))


@app.route('/add_material/<int:course_id>', methods=['GET', 'POST'])
@login_required
def add_material(course_id):
    add_material_form = AddMaterial()
    course = Course.query.get(course_id)
    if add_material_form.validate_on_submit():
        filename = add_material_form.file.data.filename
        material = Material(name=filename,
                            reference='files/materials/',
                            course=course)

        db.session.add(material)
        db.session.commit()

        material.reference += str(material.id) + filename

        db.session.commit()
        add_material_form.file.data.save(os.path.join(app.config['UPLOAD_FOLDER'], material.reference))
        return redirect('/courses/' + str(course_id))
    return render_template("add_material_form.html",
                           user=current_user,
                           course=course,
                           add_material_form=add_material_form)


@app.route('/add_lab/<int:course_id>', methods=['GET', 'POST'])
@login_required
def add_lab(course_id):
    add_lab_form = AddActivity()
    course = Course.query.get(course_id)
    if add_lab_form.validate_on_submit():
        filename = add_lab_form.file.data.filename
        activity = Activity(name=add_lab_form.activity_name.data,
                            cost=add_lab_form.cost.data,
                            reference='files/activities/',
                            course=course)

        db.session.add(activity)
        db.session.commit()

        activity.reference += str(activity.id) + filename

        db.session.commit()

        add_lab_form.file.data.save(os.path.join(app.config['UPLOAD_FOLDER'], activity.reference))

        return redirect('/courses/' + str(course_id))
    return render_template("add_lab_form.html",
                           user=current_user,
                           course=course,
                           add_lab_form=add_lab_form
                           )


@app.route('/add_student/<int:course_id>', methods=['GET', 'POST'])
@login_required
def add_student(course_id):
    add_student_form = AddStudentToCourse()
    q_factory = get_all_students(course_id)
    add_student_form.student.query_factory = q_factory
    this_course = Course.query.get(course_id)
    if add_student_form.validate_on_submit():
        this_course.students.append(add_student_form.student.data)
        db.session.commit()
        return redirect('/courses/' + str(course_id))
    return render_template("add_student.html",
                           user=current_user,
                           course=this_course,
                           add_student_form=add_student_form)


@app.route('/activity/<int:activity_id>', methods=['GET', 'POST'])
@login_required
def activity(activity_id):
    activity = Activity.query.get(activity_id)
    add_material_form = AddMaterial()
    student_work = StudentWork.query.get((activity_id, current_user.id))
    if add_material_form.validate_on_submit():
        filename = add_material_form.file.data.filename
        student_work = StudentWork(name=filename,
                                   reference='files/student_labs/' + str(current_user.id) + str(activity_id) + filename)
        student_work.student = current_user
        student_work.activity = activity
        db.session.commit()

        add_material_form.file.data.save(os.path.join(app.config['UPLOAD_FOLDER'], student_work.reference))
    return render_template('activity.html',
                           user=current_user,
                           activity=activity,
                           student_work=student_work,
                           add_material_form=add_material_form
                           )


@app.route('/t_activity/<int:course_id>/<int:activity_id>', methods=['GET', 'POST'])
@login_required
def t_activity(course_id, activity_id):
    activity = Activity.query.get(activity_id)
    course = Course.query.get(course_id)

    add_mark_form = AddMark()
    add_mark_form.student.query_factory = get_students_in_course(course_id)
    if add_mark_form.validate_on_submit():
        student = add_mark_form.student.data
        work = StudentWork.query.get((activity.id, student.id))
        work.mark = add_mark_form.mark.data
        work.comment = add_mark_form.comment.data
        db.session.commit()
        return redirect('/t_activity/' + str(course_id) + '/' + str(activity_id))
    return render_template('t_activity.html',
                           user=current_user,
                           activity=activity,
                           course=course,
                           add_mark_form=add_mark_form
                           )


@app.route('/courses/<int:course_id>/result', methods=['GET', 'POST'])
def concrete_course_result(course_id):
    pass
    # if g.user is not None and g.user.is_authenticated:
    #
    #     if g.user.role == 1:
    #         result = DBManager().get_course_result_for_student(course_id, g.user.id)
    #         return render_template('s_course_result.html', user=g.user,
    #                                course_id=str(course_id),
    #                                result=result
    #                                )
    #     if g.user.role == 2:
    #         course_result = DBManager.get_course_result(course_id)
    #         productivity = DBManager.get_course_productivity(course_id)
    #         return render_template('t_course_result.html', user=g.user,
    #                                course_id=str(course_id),
    #                                result=course_result,
    #                                productivity=productivity
    #                                )
    # return redirect("/login")


@app.route('/my_progress', methods=['GET', 'POST'])
@login_required
def progress():
    my_statistic = get_student_results(current_user.id)
    return render_template('my_progress.html',
                           user=current_user,
                           statistic=my_statistic)

