from django.urls import path
from . import views

app_name = 'announce'

urlpatterns = [
    path('messages/', views.message_list, name='message_list'),
path('messages/<int:message_id>/mark-as-read/', views.mark_as_read, name='mark_as_read'),
path('send_message/', views.message_view,name='send_message'),
path('announcements/student/', views.student_announcements, name='student_announcements'),
path('announcements/detail/<int:announcement_id>/', views.announcement_detail, name='announcement_detail'),
path('announcements/<int:announcement_id>/announcement_state/', views.announcement_state, name='announcement_state'),
path('announcements/', views.announcements,name='announcements'),
path('markunread/<int:announcement_id>/', views.mark_unread, name='mark_unread'),
path('reminder/<int:announcement_id>/', views.reminder, name='reminder'),
path('messages/mark-all-as-read/', views.mark_all_as_read, name='mark_all_as_read'),
path('messages/view/<int:message_id>/', views.handle_view_request, name='handle_view_request'),
path('load_receivers/', views.load_receivers, name='load_receivers'),
# path('message/<int:message_id>/detail/', views.message_detail, name='message_detail'),
#     path('announcement/<int:announcement_id>/detail/', views.announcement_detail, name='announcement_detail'),
]
