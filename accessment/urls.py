from django.urls import path
from . import views

app_name = 'accessment'

urlpatterns = [
path('confirm-info/', views.confirm_info, name='confirm_info'),
    path('exams/', views.exam_list, name='exam_list'),
    path('exams/<int:exam_id>/start/', views.start_exam, name='start_exam'),
    path('exams/<int:exam_id>/page/<int:order>/', views.exam_page, name='exam_page'),
    #path('exams/save_answers/', views.save_answers, name='save_answers'),
    path('exams/next_page/<int:exam_id>/<int:order>/', views.next_page, name='next_page'),
    path('exams/save_page/<int:exam_id>/<int:order>/', views.save_page, name='save_page'),
    path('exams/submit_exam/', views.submit_exam, name='submit_exam'),
    path('exams/<int:exam_id>/result/', views.exam_result, name='exam_result'),
path('exams/update_play_count/', views.update_play_count, name='update_play_count'),
path('update_remaining_time/<int:page_record_id>/', views.update_remaining_time, name='update_remaining_time'),

    ]