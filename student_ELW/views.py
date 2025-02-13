from django.shortcuts import render
from django.urls import reverse
from urllib.parse import urlencode
from django.http import HttpResponseRedirect
from django.shortcuts import render, HttpResponse, redirect, get_object_or_404


# Create your views here.
# 学生端主页展示
def student_index(request):
    role = request.session.get('role','none')
    if role == 'student':
        if request.session.get('is_login', None):
            return render(request, 'students/index.html', {
                'username': request.session['username'],
            })
        return redirect('login')
    else:
        return redirect('login')