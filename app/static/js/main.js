/**
 * Created by User on 24.04.2017.
 */
(function ($, undefined) {
    $(function () {
        $("#change_answer_button").click(function () {

            if ($("#change_answer_form").is(':visible')) {
                $("#change_answer_form").hide();
            }
            else {
                $("#change_answer_form").show();
            }

        })


        $("#course_result_marks").click(function () {

            if ($("#student_marks").is(':visible')) {
                $("#student_marks").hide();
            }
            else {
                $("#student_marks").show();
            }

        })

        $("#students_productivity").click(function () {

            if ($("#student_productivity").is(':visible')) {
                $("#student_productivity").hide();
            }
            else {
                $("#student_productivity").show();
            }

        })

        $("#rank_teacher").click(function () {

            if ($("#teacher_popularity").is(':visible')) {
                $("#teacher_popularity").hide();
            }
            else {
                $("#teacher_popularity").show();
            }

        })

        $("#course_statistic").click(function () {

            if ($("#statistic_for_course").is(':visible')) {
                $("#statistic_for_course").hide();
            }
            else {
                $("#statistic_for_course").show();
            }

        })


        $("#course_materials_paragraph").click(function () {

            if ($("#course_materials_list").is(':visible')) {
                $("#course_materials_list").hide();
            }
            else {
                $("#course_materials_list").show();
            }

        })

        $("#course_activities_paragraph").click(function () {

            if ($("#course_activities_list").is(':visible')) {
                $("#course_activities_list").hide();
            }
            else {
                $("#course_activities_list").show();
            }

        })

        $("#course_students_paragraph").click(function () {

            if ($("#course_students_list").is(':visible')) {
                $("#course_students_list").hide();
            }
            else {
                $("#course_students_list").show();
            }

        })

        $("#course_popularity").click(function () {

            if ($("#popularity_for_course").is(':visible')) {
                $("#popularity_for_course").hide();
            }
            else {
                $("#popularity_for_course").show();
            }

        })

        $(".mark_field").click(function () {

            window.location.replace("https://www.google.com.ua/?gfe_rd=cr&dcr=0&ei=CBkxWqWgA6ji8AfWvaKADQ")


        })

        window.onresize = function (event) {
            $('#mobileMenu').hide();
        }
        $(document).scroll(function () {
            if ($(document).width() > 785) {
                if ($(document).scrollTop() > $('header').height() + 10) {
                    $('nav').addClass('fixed');
                }
                else {
                    $('nav').removeClass('fixed');
                }
            }
        })

    })
})(jQuery)