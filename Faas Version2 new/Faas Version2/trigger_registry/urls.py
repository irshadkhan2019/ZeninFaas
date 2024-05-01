from django.urls import path, include
from . import views

app_name = "trigger_registry"

urlpatterns = [
    path('register-trigger/', views.register_trigger, name='register_trigger'),
    path('list/', views.trigger_list, name='trigger_list'),
  
]