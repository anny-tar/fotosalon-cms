from django.urls import path
from . import panel_views

urlpatterns = [
    path('', panel_views.review_list, name='list'),
    path('<int:pk>/approve/', panel_views.review_approve, name='approve'),
    path('<int:pk>/hide/', panel_views.review_hide, name='hide'),
    path('<int:pk>/delete/', panel_views.review_delete, name='delete'),
    path('<int:pk>/reply/', panel_views.review_reply, name='reply'),
]