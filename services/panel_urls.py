from django.urls import path
from . import panel_views

urlpatterns = [
    path('', panel_views.service_list, name='list'),
    path('create/', panel_views.service_create, name='create'),
    path('<int:pk>/edit/', panel_views.service_edit, name='edit'),
    path('<int:pk>/delete/', panel_views.service_delete, name='delete'),
    path('<int:pk>/toggle/', panel_views.service_toggle, name='toggle'),
    path('reorder/', panel_views.service_reorder, name='reorder'),
]