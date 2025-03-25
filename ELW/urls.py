from django.urls import path
from . import views

urlpatterns = [
    path(route='test_page/', view=views.test_page, name='test_page'),

    path('index/', views.teacher_index, name='teacher_index'),

    path('course/', views.teacher_course, name='teacher_course'),

    path('class/', views.teacher_class, name='teacher_class'),



    path('week_task/', views.teacher_week_task, name='teacher_week_task'),

    path('week_task_package_add/', views.teacher_week_task_package_add, name='teacher_week_task_package_add'),

    path('week_file_import/', views.teacher_week_file_import, name='teacher_week_file_import'),



    path('question_bank/', views.teacher_question_bank, name='teacher_question_bank'),

    path('delete_material/<int:material_id>', views.teacher_delete_material, name='teacher_delete_material'),

    path('edit_question/<int:id>/<int:material_id>/<str:question_type>', views.teacher_edit_question, name='teacher_edit_question'),

    path('page_create/<int:material_id>', views.teacher_page_create, name='teacher_page_create'),

    path('page_save/<int:material_id>', views.teacher_page_save, name='teacher_page_save'),



    path('exam_bank/', views.teacher_exam_bank, name='teacher_exam_bank'),

    path('exam_detail/<int:unit_id>/', views.teacher_exam_detail, name='teacher_exam_detail'),

    path('exam_edit/<int:unit_id>/<int:validation>/', views.teacher_exam_edit, name='teacher_exam_edit'),

    path('exam_resave/<int:unit_id>/', views.teacher_exam_resave, name='teacher_exam_resave'),

    path('exam_delete/<int:unit_id>/', views.teacher_exam_delete, name='teacher_exam_delete'),

    path('exam_management/', views.teacher_exam_management, name='teacher_exam_management'),



    path('forum/', views.teacher_forum, name='teacher_forum'),

    # path('teacher/task_package_add', views.teacher_question_add, name='teacher_question_add'),

    path('task_package_add/', views.teacher_task_package_add, name='teacher_task_package_add'),

    path('media_material_detail/<int:material_id>/', views.teacher_media_material_detail, name='teacher_media_material_detail'),



    path('question_add/', views.teacher_question_add, name='teacher_question_add'),

    path('question_type/', views.teacher_question_type, name='teacher_question_type'),

    path('choice/', views.teacher_choice, name='teacher_choice'),

    path('matching/', views.teacher_matching, name='teacher_matching'),

    path('correction/', views.teacher_correction, name='teacher_correction'),

    path('integration/', views.question_integration, name='question_integration'),

]