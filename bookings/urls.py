from django.urls import path
from . import views

urlpatterns = [
    path('', views.booking_form, name='booking_form'),
    path('slots/', views.get_slots, name='get_slots'),
    path('success/', views.booking_success, name='booking_success'),
]