from django.urls import path
from .views import bosh_sahifa_view

app_name = 'talim'

urlpatterns = [
    # Asosiy sahifa (http://127.0.0.1:8000/)
    path('', bosh_sahifa_view, name='bosh_sahifa'),
]