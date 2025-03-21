"""
URL configuration for Teacher_query project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from Query import views
app_name = 'Query'
urlpatterns = [
    # path('admin/', admin.site.urls),


    # --------------- 检索总面板 ----------------
    path('query/', views.query, name='query'),




    # --------------- 学习记录管理 ----------------
    path('learning/search/', views.student_learning_search, name='student_learning_search'),
    path('assignments/<int:student_id>/', views.assignment_unit, name='assignment_unit'),
    path('unit/<int:unit_id>/detail/<int:student_id>/', views.unit_detail, name='unit_detail'),
    path('update-integrity-score/', views.update_integrity_score, name='update_integrity_score'),
    path('update-question-score/', views.update_question_score, name='update_question_score'),
    # path('update-unit-score/', views.update_unit_score, name='update_unit_score'),
    path('unit/<int:unit_id>/student/<int:student_id>/delete_answer_records/', views.delete_answer_records,
         name='delete_answer_records'),
    path('unit/<int:unit_id>/student/<int:student_id>/delete_media_records/', views.delete_media_records,
         name='delete_media_records'),



    # --------------- 考勤管理+调课补课管理 ----------------
    path('attendance_query/', views.attendance_query, name='attendance_query'),
    path('adjust-schedule/', views.adjust_class_schedule, name='adjust_schedule'),
    path('batch_delete_schedule_adjustments/', views.batch_delete_schedule_adjustments, name='batch_delete_schedule_adjustments'),
    path('batch_delete_schedule_additions/', views.batch_delete_schedule_additions, name='batch_delete_schedule_additions'),
    path('class_seat_plan/<int:class_id>/', views.class_seat_plan, name='class_seat_plan'),
    path('update-seat-number/', views.update_seat_number, name='update-seat-number'),



    # --------------- 数据统计分析 ----------------
    path('statistic/search/', views.class_statistic_search, name='class_statistic_search'),
    path('units/<int:class_id>/', views.class_unit, name='class_unit'),
    path('unit/<int:unit_id>/statistic/<int:class_id>/', views.unit_statistic, name='unit_statistic'),
    path('statistic_announce/<int:class_id>/', views.statistic_announce, name='statistic_announce'),

]