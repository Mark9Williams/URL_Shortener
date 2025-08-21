# shortener/urls.py
from django.urls import path
from . import views


urlpatterns = [
path('', views.home, name='home'),
 path('analytics/', views.link_analytics, name='link_analytics'),
path('signup/', views.signup, name='signup'),


# Keep this last so it doesn't swallow other routes
path('<str:code>/', views.redirect_code, name='redirect'),
]