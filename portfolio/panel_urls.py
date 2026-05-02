from django.urls import path
from . import panel_views

urlpatterns = [
    path('', panel_views.portfolio_list, name='list'),
    path('upload/', panel_views.portfolio_upload, name='upload'),
    path('<int:pk>/toggle/', panel_views.portfolio_toggle, name='toggle'),
    path('<int:pk>/delete/', panel_views.portfolio_delete, name='delete'),
    path('genres/', panel_views.genre_list, name='genre_list'),
    path('genres/create/', panel_views.genre_create, name='genre_create'),
    path('genres/<int:pk>/delete/', panel_views.genre_delete, name='genre_delete'),
]