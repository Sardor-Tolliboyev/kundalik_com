from django.urls import path
from .views import bosh_sahifa_view, oqituvchi_profil_view

app_name = 'talim'

urlpatterns = [
    path('', bosh_sahifa_view, name='bosh_sahifa'),
    path('profil/oqituvchi/', oqituvchi_profil_view, name='oqituvchi_profil'),
]