from django.urls import path
from .views import AdminUserAPIView, RoleAPIView, LevelAPIView, CategoryMaterialAPIView

urlpatterns = [

    path('users/', AdminUserAPIView.as_view(), name='admin_users'),
    path('users/<int:user_id>/', AdminUserAPIView.as_view(), name='admin_user_detail'),
    path('roles/', RoleAPIView.as_view(), name='admin_roles'),
    path('roles/<int:role_id>/', RoleAPIView.as_view(), name='admin_roles_detail'),
    path('levels/', LevelAPIView.as_view(), name='admin_levels'),
    path('levels/<int:level_id>/', LevelAPIView.as_view(), name='admin_levels_detail'),
    path('categories/', CategoryMaterialAPIView.as_view(), name='admin_categories'),
    path('categories/<int:categories_id>/', CategoryMaterialAPIView.as_view(), name='admin_categories_detail'),

]