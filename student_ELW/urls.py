from django.urls import path
from . import views

app_name = 'student_ELW'

urlpatterns = [
    path('student_index/', views.student_index, name='student_index'),

]