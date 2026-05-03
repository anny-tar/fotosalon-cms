from django.urls import path
from . import panel_views

urlpatterns = [
    path('', panel_views.settings_view, name='settings'),
    path('contact/', panel_views.contact_settings, name='contact'),
    path('contact/create/', panel_views.contact_create, name='contact_create'),
    path('contact/<int:pk>/edit/', panel_views.contact_edit, name='contact_edit'),
    path('contact/<int:pk>/delete/', panel_views.contact_delete, name='contact_delete'),
    path('contact/<int:pk>/toggle/', panel_views.contact_toggle, name='contact_toggle'),
    path('contact/reorder/', panel_views.contact_reorder, name='contact_reorder'),
    path('smtp/', panel_views.smtp_settings, name='smtp'),
    path('sections/', panel_views.sections_list, name='sections'),
    path('sections/create/', panel_views.section_create, name='section_create'),
    path('sections/<int:pk>/edit/', panel_views.section_edit, name='section_edit'),
    path('sections/<int:pk>/delete/', panel_views.section_delete, name='section_delete'),
    path('sections/<int:pk>/toggle/', panel_views.section_toggle, name='section_toggle'),
    path('sections/reorder/', panel_views.section_reorder, name='section_reorder'),
]