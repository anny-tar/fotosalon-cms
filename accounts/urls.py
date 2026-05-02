from django.urls import path, include
from . import views

app_name = 'panel'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('login/', views.panel_login, name='login'),
    path('logout/', views.panel_logout, name='logout'),

    # Разделы панели
    path('bookings/', include('bookings.panel_urls')),
    path('schedule/', include('bookings.schedule_urls')),
    path('portfolio/', include('portfolio.panel_urls')),
    path('products/', include('products.panel_urls')),
    path('services/', include('services.panel_urls')),
    path('news/', include('news.panel_urls')),
    path('reviews/', include('reviews.panel_urls')),
    path('feedback/', include('feedback.panel_urls')),
    path('users/', include('accounts.user_urls')),
    path('settings/', include('core.panel_urls')),
]