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
#导入Account视图（用于登录相关功能）
from Account import views as account_views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import announce.routing
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from Account.api.views import LoginView, RefreshTokenView, LogoutView, CurrentUserView, TokenObtainPairViewWithTag, ChangePasswordView
from Account.api import user_views
from ELW.api import views as content_views
from forum.api import views as forum_views
from announce.api import views as announce_views
from accessment.api import views as exam_views
from Query.api import views as query_views
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView


urlpatterns = [
    path('admin/', admin.site.urls),

    # Legacy views (keep for backward compatibility)
    path(route='login/', view=account_views.user_login, name='login'),
    path(route='logout/', view=account_views.log_out, name='logout'),
    path('update_last_activity/', view=account_views.update_last_activity, name='update_last_activity'),
    
    # API Documentation (Swagger/OpenAPI)
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    
    # API routes
    path('api/v1/auth/', include([
        path('login/', LoginView.as_view(), name='api_login'),
        path('token/', TokenObtainPairViewWithTag.as_view(), name='token_obtain_pair'),  # Keep for compatibility
        path('token/refresh/', RefreshTokenView.as_view(), name='api_token_refresh'),
        path('refresh/', RefreshTokenView.as_view(), name='api_refresh'),  # Alias
        path('logout/', LogoutView.as_view(), name='api_logout'),
        path('user/', CurrentUserView.as_view(), name='api_current_user'),
        path('change-password/', ChangePasswordView.as_view(), name='api_change_password'),
    ])),
    path('api/v1/users/', include([
        # 创建 API（用于测试，不需要认证）
        path('courses/create/', user_views.CourseCreateView.as_view(), name='api_course_create'),
        path('teachers/create/', user_views.TeacherCreateView.as_view(), name='api_teacher_create'),
        path('classes/create/', user_views.ClassCreateView.as_view(), name='api_class_create'),
        path('students/create/', user_views.StudentCreateView.as_view(), name='api_student_create'),
        # 查询 API（需要认证）
        path('students/', include([
            path('', user_views.StudentListView.as_view(), name='api_student_list'),
            path('<int:student_id>/', user_views.StudentDetailView.as_view(), name='api_student_detail'),
            path('<int:student_id>/update/', user_views.StudentUpdateView.as_view(), name='api_student_update'),
        ])),
        path('teachers/', include([
            path('', user_views.TeacherListView.as_view(), name='api_teacher_list'),
            path('<int:teacher_id>/', user_views.TeacherDetailView.as_view(), name='api_teacher_detail'),
            path('<int:teacher_id>/update/', user_views.TeacherUpdateView.as_view(), name='api_teacher_update'),
        ])),
        path('classes/', include([
            path('', user_views.ClassListView.as_view(), name='api_class_list'),
            path('<int:class_id>/', user_views.ClassDetailView.as_view(), name='api_class_detail'),
            path('<int:class_id>/students/', user_views.ClassStudentsView.as_view(), name='api_class_students'),
        ])),
    ])),
    path('api/v1/content/', include([
        path('media-materials/', include([
            path('', content_views.MediaMaterialListView.as_view(), name='api_media_material_list'),
            path('<int:material_id>/', content_views.MediaMaterialDetailView.as_view(), name='api_media_material_detail'),
            path('<int:material_id>/questions/', content_views.MediaMaterialQuestionsView.as_view(), name='api_media_material_questions'),
        ])),
        path('main-questions/', include([
            path('<int:question_id>/', content_views.MainQuestionDetailView.as_view(), name='api_main_question_detail'),
            path('<int:question_id>/sub-questions/', content_views.MainQuestionSubQuestionsView.as_view(), name='api_main_question_sub_questions'),
        ])),
        path('sub-questions/<int:sub_question_id>/', content_views.SubQuestionDetailView.as_view(), name='api_sub_question_detail'),
        path('units/', include([
            path('', content_views.UnitListView.as_view(), name='api_unit_list'),
            path('<int:unit_id>/', content_views.UnitDetailView.as_view(), name='api_unit_detail'),
            path('<int:unit_id>/pages/', content_views.UnitPagesView.as_view(), name='api_unit_pages'),
        ])),
        path('pages/', include([
            path('', content_views.PaperPageListView.as_view(), name='api_page_list'),
            path('<int:page_id>/', content_views.PaperPageDetailView.as_view(), name='api_page_detail'),
            path('<int:page_id>/questions/', content_views.PageQuestionsView.as_view(), name='api_page_questions'),
        ])),
    ])),
    path('api/v1/forum/', include([
        path('posts/', include([
            path('', forum_views.PostListView.as_view(), name='api_post_list'),
            path('<int:post_id>/', forum_views.PostDetailView.as_view(), name='api_post_detail'),
            path('<int:post_id>/comments/', forum_views.CommentListView.as_view(), name='api_post_comments'),
        ])),
        path('posts/create/', forum_views.PostCreateView.as_view(), name='api_post_create'),
        path('posts/<int:post_id>/update/', forum_views.PostUpdateView.as_view(), name='api_post_update'),
        path('posts/<int:post_id>/delete/', forum_views.PostDeleteView.as_view(), name='api_post_delete'),
        path('posts/<int:post_id>/comments/create/', forum_views.CommentCreateView.as_view(), name='api_comment_create'),
        path('comments/<int:comment_id>/', include([
            path('update/', forum_views.CommentUpdateView.as_view(), name='api_comment_update'),
            path('delete/', forum_views.CommentDeleteView.as_view(), name='api_comment_delete'),
        ])),
    ])),
    path('api/v1/announcements/', include([
        path('', announce_views.AnnouncementListView.as_view(), name='api_announcement_list'),
        path('<int:announcement_id>/', announce_views.AnnouncementDetailView.as_view(), name='api_announcement_detail'),
        path('create/', announce_views.AnnouncementCreateView.as_view(), name='api_announcement_create'),
        path('<int:announcement_id>/update/', announce_views.AnnouncementUpdateView.as_view(), name='api_announcement_update'),
        path('<int:announcement_id>/delete/', announce_views.AnnouncementDeleteView.as_view(), name='api_announcement_delete'),
    ])),
    path('api/v1/messages/', include([
        path('', announce_views.MessageListView.as_view(), name='api_message_list'),
        path('<int:message_id>/', announce_views.MessageDetailView.as_view(), name='api_message_detail'),
    ])),
    path('api/v1/exams/', include([
        path('', exam_views.ExamListView.as_view(), name='api_exam_list'),
        path('<int:exam_id>/', exam_views.ExamDetailView.as_view(), name='api_exam_detail'),
        path('<int:exam_id>/start/', exam_views.ExamStartView.as_view(), name='api_exam_start'),
        path('<int:exam_id>/pages/<int:page_order>/', exam_views.ExamPageView.as_view(), name='api_exam_page'),
        path('<int:exam_id>/submit/', exam_views.ExamSubmitView.as_view(), name='api_exam_submit'),
        path('<int:exam_id>/result/', exam_views.ExamResultView.as_view(), name='api_exam_result'),
        path('<int:exam_id>/media-play/', exam_views.MediaPlayUpdateView.as_view(), name='api_media_play_update'),
    ])),
    path('api/v1/exams/pages/<int:page_record_id>/answers/', exam_views.ExamPageAnswersSaveView.as_view(), name='api_exam_page_answers_save'),
    path('api/v1/query/', include([
        path('attendance/', query_views.AttendanceQueryView.as_view(), name='api_attendance_query'),
        path('learning-records/', query_views.StudentLearningRecordView.as_view(), name='api_learning_records'),
        path('statistics/', include([
            path('class/<int:class_id>/', query_views.ClassStatisticView.as_view(), name='api_class_statistic'),
            path('unit/<int:unit_id>/', query_views.UnitStatisticView.as_view(), name='api_unit_statistic'),
        ])),
        path('overdue-rules/', include([
            path('', query_views.OverdueRuleListView.as_view(), name='api_overdue_rule_list'),
            path('<int:rule_id>/', query_views.OverdueRuleDetailView.as_view(), name='api_overdue_rule_detail'),
        ])),
    ])),
    
    # 分发路由
    path('teacher/', include('ELW.urls')),
    path('student/', include('student_ELW.urls')),
    path('query/', include('Query.urls')),
    
    # Forum, announce, accessment
    path('forum/', include('forum.urls')),
    path('announce/', include('announce.urls')),
    path('accessment/', include('accessment.urls')),
    path('stu_practice/', include('stu_practice.urls')),
]

# 开发环境下提供静态文件和媒体文件服务
if settings.DEBUG:
    # 使用Django的staticfiles应用来服务静态文件
    urlpatterns += staticfiles_urlpatterns()
    # 添加媒体文件服务
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


application = ProtocolTypeRouter({
    'http': get_asgi_application(),
    'websocket': AuthMiddlewareStack(
        URLRouter(
            announce.routing.websocket_urlpatterns
        )
    ),
})

