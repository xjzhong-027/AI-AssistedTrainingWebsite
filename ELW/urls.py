from django.urls import path
from . import views

urlpatterns = [
    path(route='test_page/', view=views.test_page, name='test_page'),

    path('index/', views.teacher_index, name='teacher_index'),

    path('course/', views.teacher_course, name='teacher_course'),

    path('class/', views.teacher_class, name='teacher_class'),

    path('question_bank/', views.teacher_question_bank, name='teacher_question_bank'),

    path('exam_bank/', views.teacher_exam_bank, name='teacher_exam_bank'),

    path('exam_management/', views.teacher_exam_management, name='teacher_exam_management'),

    path('forum/', views.teacher_forum, name='teacher_forum'),

    # path('teacher/task_package_add', views.teacher_question_add, name='teacher_question_add'),

    path('task_package_add/', views.teacher_task_package_add, name='teacher_task_package_add'),

    path('question_add/', views.teacher_question_add, name='teacher_question_add'),

    path('question_type/', views.teacher_question_type, name='teacher_question_type'),

    path('matching/', views.teacher_matching, name='teacher_matching'),

    path('correction/', views.teacher_correction, name='teacher_correction'),

]