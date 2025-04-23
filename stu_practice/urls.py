from django.urls import path
from . import views

app_name = 'stu_practice'

urlpatterns = [
    # path('/confirm-info/', views.confirm_info, name='confirm_info'),
    path('practices/', views.practice_list, name='practice_list'),
    path('practices/<int:practice_id>/start/', views.start_practice, name='start_practice'),
    path('practices/<int:practice_id>/page/<int:order>/', views.practice_page, name='practice_page'),
    path('practices/next_page/<int:practice_id>/<int:order>/', views.next_page, name='next_page'),
    path('practices/save_page/<int:practice_id>/<int:order>/', views.save_page, name='save_page'),
    path('practices/submit_practice/', views.submit_practice, name='submit_practice'),
    path('practices/<int:practice_id>/result/', views.practice_result, name='practice_result'),
    path('practices/update_play_count/', views.update_play_count, name='update_play_count'),
    path('update_remaining_time/<int:page_record_id>/', views.update_remaining_time, name='update_remaining_time'),
    path('practices/dashboard/', views.student_dashboard, name='dashboard'),
    path('change-password/', views.change_password, name='change_password'),
]