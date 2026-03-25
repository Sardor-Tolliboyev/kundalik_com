from django.urls import path
from django.contrib.auth import views as auth_views
from .views import shaxsiy_profil_view, login_redirect_view, shaxsiy_profil_tahrir_view

app_name = 'hisoblar' # BU SHART!

urlpatterns = [
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('profil/', shaxsiy_profil_view, name='shaxsiy_profil'),
    path('profil/tahrir/', shaxsiy_profil_tahrir_view, name='shaxsiy_profil_tahrir'),
    path('kirish-muvaffaqiyatli/', login_redirect_view, name='login_redirect'),
]
