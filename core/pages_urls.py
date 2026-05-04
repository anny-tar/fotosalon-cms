from django.urls import path
from . import pages_views

urlpatterns = [
    path('', pages_views.pages_list, name='list'),
    path('<str:page>/sections/', pages_views.sections_list, name='sections'),
    path('<str:page>/sections/create/', pages_views.section_create, name='section_create'),
    path('sections/<int:pk>/edit/', pages_views.section_edit, name='section_edit'),
    path('sections/<int:pk>/delete/', pages_views.section_delete, name='section_delete'),
    path('sections/<int:pk>/toggle/', pages_views.section_toggle, name='section_toggle'),
    path('sections/<int:pk>/draft/', pages_views.section_draft_save, name='section_draft'),
    path('sections/<int:pk>/publish/', pages_views.section_publish, name='section_publish'),
    path('sections/reorder/', pages_views.section_reorder, name='section_reorder'),
    path('sections/preview/', pages_views.section_preview, name='section_preview'),
    path('sections/upload-image/', pages_views.section_upload_image, name='section_upload_image'),
]