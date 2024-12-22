from django.urls import path
from .views import AdminUserAPIView, RoleAPIView, LevelAPIView, CategoryMaterialAPIView, ModuleAPIView, TopicAPIView

urlpatterns = [

    path('users/', AdminUserAPIView.as_view(), name='admin_users'),
    path('users/<int:user_id>/', AdminUserAPIView.as_view(), name='admin_user_detail'),

    path('roles/', RoleAPIView.as_view(), name='admin_roles'),
    path('roles/<int:role_id>/', RoleAPIView.as_view(), name='admin_roles_detail'),

    path('levels/', LevelAPIView.as_view(), name='admin_levels'),
    path('levels/<int:level_id>/', LevelAPIView.as_view(), name='admin_levels_detail'),

    path('categoriesmaterial/', CategoryMaterialAPIView.as_view(), name='admin_categories'),
    path('categoriesmaterial/<int:category_id>/', CategoryMaterialAPIView.as_view(), name='admin_categories_detail'),

    path('modules/', ModuleAPIView.as_view(), name='admin_module'),
    path('modules/<int:module_id>/', ModuleAPIView.as_view(), name='admin_module_detail'),

    path('topics/', TopicAPIView.as_view(), name='admin_topic'),
    path('topics/<int:topic_id>/', TopicAPIView.as_view(), name='admin_topic_detail'),



]