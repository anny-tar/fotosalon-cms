from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.dashboard, name='panel_dashboard'),
    path('login/', views.panel_login, name='panel_login'),
    path('logout/', views.panel_logout, name='panel_logout'),

    path('bookings/', include(('bookings.panel_urls', 'bookings_panel'))),
    path('schedule/', include(('bookings.schedule_urls', 'schedule_panel'))),
    path('pages/', include(('core.pages_urls', 'pages_panel'))),
    path('portfolio/', include(('portfolio.panel_urls', 'portfolio_panel'))),
    path('products/', include(('products.panel_urls', 'products_panel'))),
    path('services/', include(('services.panel_urls', 'services_panel'))),
    path('news/', include(('news.panel_urls', 'news_panel'))),
    path('reviews/', include(('reviews.panel_urls', 'reviews_panel'))),
    path('feedback/', include(('feedback.panel_urls', 'feedback_panel'))),
    path('users/', include(('accounts.user_urls', 'users_panel'))),
    path('settings/', include(('core.panel_urls', 'settings_panel'))),
]