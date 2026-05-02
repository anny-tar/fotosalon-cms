from django.urls import path
from . import schedule_views

urlpatterns = [
    path('', schedule_views.schedule_grid, name='grid'),
    path('slot/create/', schedule_views.slot_create, name='slot_create'),
    path('slot/<int:pk>/toggle/', schedule_views.slot_toggle_block, name='slot_toggle'),
    path('slot/<int:pk>/delete/', schedule_views.slot_delete, name='slot_delete'),
    path('generate/', schedule_views.slots_generate, name='generate'),
]