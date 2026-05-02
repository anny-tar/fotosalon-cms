from django.urls import path
from . import panel_views

urlpatterns = [
    path('', panel_views.feedback_list, name='list'),
    path('<int:pk>/', panel_views.feedback_detail, name='detail'),
    path('<int:pk>/read/', panel_views.feedback_mark_read, name='mark_read'),
    path('<int:pk>/delete/', panel_views.feedback_delete, name='delete'),
]