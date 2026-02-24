from django.urls import path
from django.contrib.auth import views as auth_views
from .views import shaxsiy_profil_view, login_redirect_view

# Ilovaning nomi (Namespace)
app_name = 'hisoblar'

urlpatterns = [
    # 1. LOGIN (KIRISH) SAHIFASI
    # as_view() ichida hech qanday nuqtalar bo'lmasligi kerak!
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    
    # 2. LOGOUT (CHIQISH)
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

    # 3. PROFIL SAHIFASI
    path('profil/', shaxsiy_profil_view, name='shaxsiy_profil'),

    # 4. LOGIN DAN KEYIN YO'NALTIRISH
    path('kirish-muvaffaqiyatli/', login_redirect_view, name='login_redirect'),
]