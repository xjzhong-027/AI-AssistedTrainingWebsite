from django.urls import path
from . import views

urlpatterns = [
    path('teacher/test_page', views.test_page, name='test_page'),

    path('teacher/index/', views.teacher_index, name='teacher_index'),

    path('teacher/course/', views.teacher_course, name='teacher_course'),

    path('teacher/class/', views.teacher_class, name='teacher_class'),

    path('teacher/question_bank', views.teacher_question_bank, name='teacher_question_bank'),

    path('teacher/exam_bank', views.teacher_exam_bank, name='teacher_exam_bank'),

    path('teacher/exam_management', views.teacher_exam_management, name='teacher_exam_management'),

    path('teacher/forum', views.teacher_forum, name='teacher_forum'),

    # path('teacher/task_package_add', views.teacher_question_add, name='teacher_question_add'),

    path('teacher/task_package_add/', views.teacher_task_package_add, name='teacher_task_package_add'),

]