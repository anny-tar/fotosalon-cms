from django.urls import path
from . import panel_views

urlpatterns = [
    path('', panel_views.settings_view, name='settings'),
    path('contact/', panel_views.contact_settings, name='contact'),
    path('smtp/', panel_views.smtp_settings, name='smtp'),
    path('sections/', panel_views.sections_list, name='sections'),
    path('sections/create/', panel_views.section_create, name='section_create'),
    path('sections/<int:pk>/edit/', panel_views.section_edit, name='section_edit'),
    path('sections/<int:pk>/delete/', panel_views.section_delete, name='section_delete'),
    path('sections/<int:pk>/toggle/', panel_views.section_toggle, name='section_toggle'),
]