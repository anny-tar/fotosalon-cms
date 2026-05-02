from django.urls import path
from . import panel_views

urlpatterns = [
    path('', panel_views.product_list, name='list'),
    path('create/', panel_views.product_create, name='create'),
    path('<int:pk>/edit/', panel_views.product_edit, name='edit'),
    path('<int:pk>/delete/', panel_views.product_delete, name='delete'),
    path('export/', panel_views.product_export, name='export'),
    path('categories/', panel_views.category_list, name='category_list'),
    path('categories/create/', panel_views.category_create, name='category_create'),
    path('categories/<int:pk>/delete/', panel_views.category_delete, name='category_delete'),
]