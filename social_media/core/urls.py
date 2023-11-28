from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('settings', views.settings, name='settings'),
    path('upload', views.upload, name='upload'),
    path('follow', views.follow, name='follow'),
    path('search', views.search, name='search'),
    path('profile/<str:pk>', views.profile, name='profile'),
    path('like-post', views.like_post, name='like-post'),
    path('signup', views.signup, name='signup'),
    path('signin', views.signin, name='signin'),
    path('logout', views.logout, name='logout'),
    path('admin_dashboard', views.admin_dashboard, name='admin_dashboard'),
    path('all_users', views.all_users, name='all_users'),
    path('all_profiles', views.all_profiles, name='all_profiles'),
    path('all_posts', views.all_posts, name='all_posts'),
    path('all_followers', views.all_followers, name='all_followers'),
    path('all_likedPosts', views.all_likedPosts, name='all_likedPosts'),
]