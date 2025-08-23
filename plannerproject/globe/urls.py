from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    # Auth routes
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.CustomLogoutView.as_view(), name='logout'),
    path('signup/', views.signup, name='signup'),
]

