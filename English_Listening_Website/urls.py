"""
URL configuration for English_Listening_Website project.

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
from django.urls import path, include
# from setuptools.extern import names

#导入ELW视图
from ELW import views, urls
from django.conf import settings
from django.conf.urls.static import static

from django.contrib import admin
from django.core.asgi import get_asgi_application
from django.urls import include, path

from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import announce.routing
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('admin/', admin.site.urls),


    path(route='login/', view=views.user_login, name='login'),
    path(route='logout/', view=views.log_out, name='logout'),
    path('update_last_activity/', view=views.update_last_activity, name='update_last_activity'),
    # path('submit_question/', view=views.submit_question, name='submit_question'),
    # 分发路由
    path('teacher/', include('ELW.urls')),
    path('student/', include('student_ELW.urls')),
    # path('create-big-question/', views.create_big_question_with_small_questions, name='create_big_question_with_small_questions'),

    path('query/', include('Query.urls')),

#forum announce accessment
path('forum/', include('forum.urls')),
    path('announce/', include('announce.urls')),
                  path('accessment/', include('accessment.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)   #添加对媒体文件的访问路由


application = ProtocolTypeRouter({
    'http': get_asgi_application(),
    'websocket': AuthMiddlewareStack(
        URLRouter(
            announce.routing.websocket_urlpatterns
        )
    ),
})

