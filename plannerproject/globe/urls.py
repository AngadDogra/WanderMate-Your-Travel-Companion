from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("export-pdf/", views.export_itinerary_pdf, name="export_pdf"),
    path("chatbot/", views.chatbot, name="chatbot"),
    path("clear-chat/", views.clear_chat, name="clear_chat"),
    # Auth routes
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.CustomLogoutView.as_view(), name='logout'),
    path('signup/', views.signup, name='signup'),
]

