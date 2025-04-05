from . import views
from django.urls import path, include
app_name = 'forum'
urlpatterns = [
    path('', views.forum, name='forum'),
    path('forum/<str:category>/', views.forum, name='forum_by_category'),
    path('post/<int:post_id>/', views.post_detail, name='post_detail'),
path('forum/question_post', views.question_post, name='question_post'),
    path('post/new/', views.post_new, name='post_new'),
    path('post/<int:post_id>/delete/', views.post_delete, name='post_delete'),
    path('comment/<int:comment_id>/delete/', views.comment_delete, name='comment_delete'),
    path('post/<int:post_id>/top/', views.post_top, name='post_top'),
path('post/<int:post_id>/comment/', views.add_comment, name='add_comment'),
path('search/', views.search_posts, name='search_posts'),
path('post/<int:post_id>/comment/<int:parent_comment_id>/', views.add_comment, name='add_reply'),
path('my_post/', views.my_post, name='my_post'),
path('post/edit/<int:post_id>/', views.post_edit, name='post_edit'),
path('non_public/', views.non_public, name='non_public'),
path('ost/<int:post_id>/change_public/', views.change_public, name='change_public'),
path('get-posts-by-question/', views.get_posts_by_question, name='get_posts_by_question'),
]

