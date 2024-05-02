from django.urls import path, include
from . import views

app_name = "authentication"

urlpatterns = [
    path("login/", views.Login,name='login'),
    path('signup/', views.Signup, name='signup'),
    path('logout/',views.Logout,name='logout'),
  
]