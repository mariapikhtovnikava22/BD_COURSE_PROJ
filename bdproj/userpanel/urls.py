from django.urls import path
from .views import *

urlpatterns = [
    path('test/', EntranceTestAPIView.as_view(), name='test'),
    path('usermodules/', UserModulesAPIView.as_view(), name='usermodules'),
    path("usertopicmodules/", ModuleTopicsTestsView.as_view(), name=""),
    path("moduletest/<int:module_id>/", ModuleTestAPIView.as_view(), name=""),
    path("submittestmodule/<int:module_id>", SubmitModuleTestAPIView().as_view(), name=""),
    path("progress/", UserProgressAPIView.as_view(), name="user-progress"),

]
