from django.urls import path, include
from . import views

app_name = "function_registry"

urlpatterns = [
  path('', views.zenin_faas, name='zenin_faas'),
  path('register-function/', views.register_function, name='register_function'),
  path('functions/', views.function_list, name='function_list'),
  
]