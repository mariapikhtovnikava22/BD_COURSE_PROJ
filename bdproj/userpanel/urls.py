from django.urls import path
from .views import *

urlpatterns = [
    path('test/', EntranceTestAPIView.as_view(), name='test'),
    
]
