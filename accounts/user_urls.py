from django.urls import path
from . import user_views

urlpatterns = [
    path('', user_views.user_list, name='list'),
    path('create/', user_views.user_create, name='create'),
    path('<int:pk>/edit/', user_views.user_edit, name='edit'),
    path('<int:pk>/toggle/', user_views.user_toggle, name='toggle'),
    path('log/', user_views.action_log, name='log'),
]