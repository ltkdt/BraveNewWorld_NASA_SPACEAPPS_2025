from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
   path('',views.home, name='home'),
   path('revClick/', views.rev_click, name='rev_click'),
   path('output/<str:neartest_location>/', views.output, name='output'),
   path('dem.html', views._3d_dem_view, name='3d_dem_view'),
   # route for chatbot page: accepts optional ?image=<url> query parameter
   #path('chatbot/', views.chatbot_view, name='chatbot'),
   # simple chat API endpoint used by chatbot.html (AJAX) -> maps to server analyze handler
   path('chat/', views.chatbot_analyze, name='chat'),
]