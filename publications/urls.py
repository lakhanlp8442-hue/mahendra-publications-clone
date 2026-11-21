from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('archives/', views.archives, name='archives'),
    path('issue/<int:issue_id>/', views.issue_detail, name='issue_detail'),
    path('article/<int:article_id>/', views.article_detail, name='article_detail'),
    path('article/<int:article_id>/download/', views.download_article, name='download_article'),
    path('submit/', views.submit_manuscript, name='submit_manuscript'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('review/<int:review_id>/', views.submit_review, name='submit_review'),
    path('editorial-board/', views.editorial_board, name='editorial_board'),
    path('about/', views.about_journal, name='about_journal'),
    path('register/', views.register_user, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='publications/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
]
