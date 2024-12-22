from django.urls import path
from .views import RegisterUserAPIView, LoginUserAPIView, UserInfoAPIView

urlpatterns = [
    path('register/', RegisterUserAPIView.as_view(), name='register'),
    path('login/', LoginUserAPIView.as_view(), name='login'),
    path('about_me/', UserInfoAPIView.as_view(), name='about_me'),
]