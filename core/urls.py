from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('theme.css', views.theme_css, name='theme_css'),
    path('about/', views.about, name='about'),
    path('contacts/', views.contacts, name='contacts'),
]