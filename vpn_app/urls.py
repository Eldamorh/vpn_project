# vpn_app/urls.py
from django.urls import path
from .views import register_view, update_user_view, login_view, dashboard_view, create_site_view, proxy_view

urlpatterns = [
    path('register', register_view, name='register'),
    path('update_user', update_user_view, name='update_user'),
    path('login', login_view, name='login'),
    path('dashboard', dashboard_view, name='dashboard'),
    path('create_site', create_site_view, name='create_site'),
    path('<str:user_site_name>/<path:routes_on_original_site>', proxy_view, name='proxy'),
]
