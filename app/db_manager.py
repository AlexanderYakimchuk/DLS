from app import db
from .models import User
from flask import g


class DBManager:
    @staticmethod
    def add_user(user):
        cursor = db.cursor()
        cursor.execute("""INSERT INTO dls.users(name, surname, "e-mail", role)
                                  VALUES (%s, %s, %s, %s)""", (user.name, user.surname, user.email, user.role))

        cursor.execute("""SELECT MAX(user_id) FROM dls.users""")

        id = cursor.fetchone()

        cursor.execute("""INSERT INTO dls.logins(user_id, login)
                                  VALUES (%s, %s)""", (id, user.login))

        cursor.execute("""INSERT INTO dls.passwords(user_id, password)
                                          VALUES (%s, %s)""", (id, user.password))
        db.commit()

    @staticmethod
    def add_course(course):
        cursor = db.cursor()
        cursor.execute("""INSERT INTO dls.course(course_name, description)
                                      VALUES (%s, %s)""", (course.course_name, course.description))
        db.commit()

    @staticmethod
    def add_user_to_course(user, course, role):
        cursor = db.cursor()
        (name, surname) = user.split(' ')

        cursor.execute("""SELECT user_id FROM dls.users
                          WHERE name = %s AND surname = %s AND role=%s""", (name, surname, role))
        user_id = cursor.fetchone()[0]
        if type(course) is int:
            course_id = course
        if type(course) is str:
            cursor.execute("""SELECT course_id FROM dls.course
                                  WHERE course_name = %s""", (course,))
            course_id = cursor.fetchone()[0]
        cursor.execute("""INSERT INTO dls.user_to_course(user_id, course_id)
                          VALUES (%s, %s)""", (user_id, course_id))
        if role == 1:
            cursor.execute("""INSERT INTO dls.teacher_in_course_history(teacher_id, course_id, object_id, object_type)
                                      VALUES (%s, %s, %s, 3)""", (g.user.id, course_id, user_id))
        db.commit()

    @staticmethod
    def get_courses():
        cursor = db.cursor()
        cursor.execute("""SELECT course_name FROM dls.course""")
        return cursor.fetchall()

    @staticmethod
    def get_courses_for_user(user_id):
        cursor = db.cursor()
        cursor.execute("""SELECT c.course_id, course_name, description
                          FROM dls.course AS c
                          JOIN dls.user_to_course AS utc
                          ON c.course_id = utc.course_id
                          WHERE user_id=%s
                            """, (user_id,))
        return cursor.fetchall()

    @staticmethod
    def get_teachers():
        cursor = db.cursor()
        cursor.execute("""SELECT name || ' ' || surname FROM dls.users WHERE role=2""")
        return cursor.fetchall()

    @staticmethod
    def add_material(material, course_id, type=None):
        cursor = db.cursor()
        cursor.execute("""INSERT INTO dls.materials(reference)
                                      VALUES(%s)""", (material,))

        cursor.execute("""SELECT MAX(material_id) FROM dls.materials""")
        material_id = cursor.fetchone()[0]
        if type and type == 2:
            cursor.execute("""UPDATE dls.materials
                              SET type=%s
                              WHERE material_id=%s""", (type, material_id))

        cursor.execute("""INSERT INTO dls.material_to_course(course_id, material_id)
                          VALUES (%s, %s)""", (course_id, material_id))

        cursor.execute("""INSERT INTO dls.teacher_in_course_history(teacher_id, course_id, object_id, object_type)
                          VALUES (%s, %s, %s, 1)""", (g.user.id, course_id, material_id))
        db.commit()
        return material_id

    @staticmethod
    def get_materials(course_id, type):
        cursor = db.cursor()
        cursor.execute("""SELECT m.material_id::VARCHAR , reference
                          FROM dls.materials AS m
                          JOIN dls.material_to_course AS mtc
                          ON m.material_id = mtc.material_id
                          WHERE mtc.course_id = %s AND type = %s""", (course_id, type))
        return cursor.fetchall()

    @staticmethod
    def get_students():
        cursor = db.cursor()
        cursor.execute("""SELECT name || ' ' || surname FROM dls.users WHERE role=1 """)
        return cursor.fetchall()

    @staticmethod
    def get_students_in_course(course_id):
        cursor = db.cursor()
        cursor.execute("""SELECT name || ' ' || surname FROM dls.users AS u
                              JOIN dls.user_to_course AS stc
                              ON u.user_id = stc.user_id
                              WHERE stc.course_id = %s
                              AND role = 1""", (course_id,))
        return cursor.fetchall()

    @staticmethod
    def add_activity(material, course_id, activity_name, cost):
        material_id = DBManager.add_material(material, course_id, 2)
        cursor = db.cursor()
        cursor.execute("""INSERT INTO dls.activities(material_id, activity_name, cost)
                          VALUES(%s, %s, %s)""", (material_id, activity_name, cost))
        cursor.execute("""SELECT MAX(activity_id) FROM dls.activities""")
        activity_id = cursor.fetchone()[0]
        cursor.execute("""INSERT INTO dls.activity_to_course(course_id, activity_id)
                          VALUES (%s, %s)""", (course_id, activity_id))

        cursor.execute("""INSERT INTO dls.teacher_in_course_history(teacher_id, course_id, object_id, object_type)
                                  VALUES (%s, %s, %s, 2)""", (g.user.id, course_id, activity_id))
        db.commit()

    @staticmethod
    def get_activities(course_id):
        cursor = db.cursor()
        cursor.execute("""SELECT a.activity_id::VARCHAR, activity_name FROM dls.activities AS a
                          JOIN dls.activity_to_course AS atc
                          ON a.activity_id = atc.activity_id
                          WHERE course_id = %s""", (course_id,))
        return cursor.fetchall()

    @staticmethod
    def get_activity(activity_id):
        cursor = db.cursor()
        cursor.execute("""SELECT activity_name, a.material_id::VARCHAR, reference, cost, name, surname, time_of_addition::timestamp(0)
                          FROM dls.activities AS a
                          JOIN dls.materials AS m 
                          ON a.material_id = m.material_id
                          JOIN dls.teacher_in_course_history as tich
                          ON (a.activity_id = tich.object_id AND tich.object_type = 2)
                          JOIN dls.users AS u
                          ON tich.teacher_id = u.user_id
                          WHERE activity_id = %s""", (activity_id,))
        return cursor.fetchone()

    @staticmethod
    def add_student_to_activity(student_id, activity_id, reference):
        cursor = db.cursor()
        cursor.execute("""SELECT * FROM dls.student_to_activity
                          WHERE student_id = %s AND activity_id = %s""", (student_id, activity_id))
        if cursor.fetchone():
            cursor.execute("""UPDATE dls.student_to_activity
                              SET reference = %s
                              WHERE student_id = %s AND activity_id = %s""", (reference, student_id, activity_id))
            cursor.execute("""UPDATE dls.student_in_activity_history
                              SET time_of_addition = now()""")
        else:
            cursor.execute("""INSERT INTO dls.student_to_activity(student_id, activity_id, reference)
                              VALUES (%s, %s, %s)""", (student_id, activity_id, reference))

            cursor.execute("""INSERT INTO dls.student_in_activity_history(student_id, activity_id)
                              VALUES (%s, %s)""", (student_id, activity_id))
        db.commit()

    @staticmethod
    def get_activity_for_student(student_id, activity_id):
        cursor = db.cursor()
        cursor.execute("""SELECT mark, reference, comment, name, surname
                          FROM dls.student_to_activity AS sta 
                          JOIN dls.teacher_in_activity_history as tiah
                          ON (sta.activity_id = tiah.activity_id and sta.student_id = tiah.student_id)
                          JOIN dls.users AS u
                          ON tiah.teacher_id = u.user_id
                          WHERE sta.student_id = %s AND sta.activity_id = %s""", (student_id, activity_id))
        return cursor.fetchone()

    @staticmethod
    def get_students_activities(course_id, activity_id):
        cursor = db.cursor()
        cursor.execute("""SELECT name, surname, reference, mark, comment, u.user_id::VARCHAR, time_of_addition::timestamp(0)
                          FROM dls.student_to_activity AS sta
                          RIGHT JOIN dls.users AS u 
                          ON sta.student_id = u.user_id
                          LEFT JOIN dls.user_to_course AS utc
                          ON u.user_id = utc.user_id
                          LEFT JOIN dls.student_in_activity_history AS siah
                          ON (utc.user_id = siah.student_id AND sta.activity_id = siah.activity_id)
                          WHERE course_id = %s AND
                          (sta.activity_id = %s OR sta.activity_id is NULL) AND
                          u.role = 1""", (course_id, activity_id))
        return cursor.fetchall()

    @staticmethod
    def add_mark(student_id, activity_id, mark, comment=None):
        cursor = db.cursor()
        cursor.execute("""UPDATE dls.student_to_activity
                            SET mark = %s,
                                comment = %s
                            WHERE student_id = %s AND
                                  activity_id = %s""", (mark, comment, student_id, activity_id))
        cursor.execute("""INSERT INTO dls.teacher_in_activity_history(teacher_id, activity_id, student_id)
                          VALUES (%s, %s, %s)""", (g.user.id, activity_id, student_id))
        db.commit()

    @staticmethod
    def get_course_result(course_id):
        cursor = db.cursor()
        cursor.execute("""select name, surname, sum(cost) as max_sum, sum(mark) as student_sum,
                            case
                                when sum(mark)/sum(cost) >= 0.95 then 'A'
                                when sum(mark)/sum(cost) >= 0.85 then 'B'
                                when sum(mark)/sum(cost) >= 0.75 then 'C'
                                when sum(mark)/sum(cost) >= 0.65 then 'D'
                                when sum(mark)/sum(cost) >= 0.6 then 'E'
                                when sum(mark)/sum(cost) < 0.6 then 'F'
                            end as mark
                            from dls.users as u
                            join dls.user_to_course as utc
                            on (u.user_id = utc.user_id and role = 1)
                            left join dls.activity_to_course as atc
                            on utc.course_id = atc.course_id
                            left join dls.activities as a
                            on atc.activity_id = a.activity_id
                            left join dls.student_to_activity as sta
                            on (a.activity_id = sta.activity_id and u.user_id = sta.student_id)
                            where utc.course_id = %s
                            group by name, surname""", (course_id,))
        return cursor.fetchall()

    @staticmethod
    def get_course_productivity(course_id):
        cursor = db.cursor()
        cursor.execute("""select activity_name,
                                min(siah.time_of_addition - tich.time_of_addition) as min_time,
                                max(siah.time_of_addition - tich.time_of_addition) as max_time,
                                avg(siah.time_of_addition - tich.time_of_addition) as avg_time
                            from dls.activities as a
                            join dls.activity_to_course as atc
                            on a.activity_id = atc.activity_id
                            join dls.user_to_course as utc
                            on atc.course_id = utc.course_id
                            join dls.users as u
                            on (utc.user_id = u.user_id and role = 1)
                            left join dls.student_in_activity_history as siah
                            on (a.activity_id = siah.activity_id and u.user_id = siah.student_id)
                            left join dls.teacher_in_course_history as tich
                            on (atc.course_id = tich.course_id and object_type = 2 and atc.activity_id = tich.object_id)
                            where utc.course_id = %s
                            group by activity_name
                            order by activity_name""", (course_id,))
        return cursor.fetchall()

    @staticmethod
    def get_teacher_popularity():
        cursor = db.cursor()
        cursor.execute("""select name,
                                    surname,
                                    count_courses,
                                    dense_rank() over(order by count_courses desc)
                            from (select name, surname, count(utc.course_id) as count_courses
                                  from dls.users as u
                                  left join dls.user_to_course as utc
                                  on u.user_id = utc.user_id
                                  where role = 2
                                 group by u.user_id, name, surname) as sq""")

        return cursor.fetchall()

    @staticmethod
    def get_courses_statistic():
        cursor = db.cursor()
        cursor.execute("""select course_name, max_score, min_stud_score, max_stud_score, (((avg_score*100)::INTEGER)::FLOAT/100)
                            from dls.course as c
                            join (
                                select course_id, avg(student_score) as avg_score, max(student_score) as max_stud_score, min(student_score) as min_stud_score
                                from (
                                    select utc.course_id, u.user_id, sum(mark) as student_score
                                    from dls.user_to_course as utc
                                    join dls.users as u
                                    on (role = 1 and utc.user_id = u.user_id)
                                    join dls.activity_to_course as atc
                                    on utc.course_id = atc.course_id
                                    left join dls.student_to_activity as sta
                                    on (u.user_id = sta.student_id and atc.activity_id = sta.activity_id)
                                    group by utc.course_id, u.user_id
                                    order by utc.course_id, u.user_id
                                ) as sq
                                group by sq.course_id
                                ) as sq1
                            on c.course_id = sq1.course_id
                            join (
                                select c.course_id, sum(cost) as max_score
                                from dls.course as c
                                join dls.activity_to_course as atc
                                on c.course_id = atc.course_id
                                join dls.activities as a
                                on atc.activity_id = a.activity_id
                                group by c.course_id
                                ) as sq2
                            on c.course_id = sq2.course_id""")

        return cursor.fetchall()

    @staticmethod
    def get_teachers_activity_history():
        cursor = db.cursor()
        cursor.execute("""select name, surname, object_type, time_of_addition::timestamp::date as date_1,  time_of_addition
                            from dls.teacher_in_course_history as tich
                            join dls.users as u
                            on tich.teacher_id = u.user_id
                            order by time_of_addition desc""")
        return cursor.fetchall()

    @staticmethod
    def get_course_result_for_student(course_id, student_id):
        cursor = db.cursor()
        cursor.execute("""select activity_name, mark, cost
                            from dls.user_to_course as utc
                            join dls.activity_to_course as atc
                            on utc.course_id = atc.course_id
                            join dls.activities as a
                            on atc.activity_id = a.activity_id
                            left join dls.student_to_activity as sta
                            on (a.activity_id = sta.activity_id and utc.user_id = sta.student_id)
                            where utc.course_id = %(course_id)s and utc.user_id = %(student_id)s
                            union
                            select 'Сумма:',
                                (select sum(mark)
                                from dls.activity_to_course as atc
                                join dls.student_to_activity as sta
                                on (atc.activity_id = sta.activity_id and sta.student_id = %(student_id)s)
                                where course_id = %(course_id)s) as sq1,
                            
                                (select sum(cost)
                                from dls.activities as a
                                join dls.activity_to_course as atc
                                on a.activity_id = atc.activity_id
                                where course_id = %(course_id)s) as sq1
                            order by activity_name""", {"student_id": student_id, "course_id": course_id})
        return cursor.fetchall()

    @staticmethod
    def get_courses_popularity():
        cursor = db.cursor()
        cursor.execute("""select course_name,
                                    count_students,
                                    dense_rank() over(order by count_students desc) as range_course
                            from (
                                select c.course_id, course_name, count(u.user_id) as count_students
                                from dls.course as c
                                left join dls.user_to_course as utc
                                on c.course_id = utc.course_id
                                left join dls.users as u
                                on (utc.user_id = u.user_id and role = 1)
                                group by c.course_id, course_name) as sq1""")
        return cursor.fetchall()

    @staticmethod
    def get_courses_statistic_for_student(student_id):
        cursor = db.cursor()
        cursor.execute("""select course_name,
                                    my_score,
                                    max_score,
                                    (my_score*100/max_score)::integer::varchar as pc
                            from dls.course as c
                            join(
                                select utc.course_id, sum(mark) as my_score
                                from dls.user_to_course as utc
                                join dls.activity_to_course as atc
                                on utc.course_id = atc.course_id
                                left join dls.student_to_activity as stc
                                on (utc.user_id = stc.student_id and atc.activity_id = stc.activity_id)
                                where utc.user_id = %(user_id)s
                                group by utc.course_id) as sq1
                            on c.course_id = sq1.course_id
                            join(
                                select atc.course_id, sum(cost) as max_score
                                from dls.activity_to_course as atc
                                join dls.activities as a
                                on atc.activity_id = a.activity_id
                                join dls.user_to_course as stc
                                on atc.course_id = stc.course_id
                                where user_id = %(user_id)s
                                group by atc.course_id) as sq2
                            on c.course_id = sq2.course_id""", {"user_id": student_id, })
        return cursor.fetchall()
