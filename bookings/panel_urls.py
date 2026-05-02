from django.urls import path
from . import panel_views

urlpatterns = [
    path('', panel_views.booking_list, name='list'),
    path('<int:pk>/', panel_views.booking_detail, name='detail'),
    path('<int:pk>/status/', panel_views.booking_change_status, name='change_status'),
    path('export/', panel_views.booking_export, name='export'),
]