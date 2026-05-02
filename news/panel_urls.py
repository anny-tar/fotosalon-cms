from django.urls import path
from . import panel_views

urlpatterns = [
    path('', panel_views.news_list, name='list'),
    path('create/', panel_views.news_create, name='create'),
    path('<int:pk>/edit/', panel_views.news_edit, name='edit'),
    path('<int:pk>/delete/', panel_views.news_delete, name='delete'),
    path('<int:pk>/photo/delete/', panel_views.news_photo_delete, name='photo_delete'),
    path('categories/', panel_views.news_category_list, name='category_list'),
    path('categories/create/', panel_views.news_category_create, name='category_create'),
    path('categories/<int:pk>/delete/', panel_views.news_category_delete, name='category_delete'),
]