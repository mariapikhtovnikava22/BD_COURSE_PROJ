from django.urls import path
from .views import *

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

    path('tests/', TestAPIView.as_view(), name='admin_test'),
    path('tests/<int:test_id>/', TestAPIView.as_view(), name='admin_test_detail'),

    path('qestions/', QuestionsAPIView.as_view(), name='admin_question'),
    path('questions/<int:question_id>/', QuestionsAPIView.as_view(), name='admin_questuion_detail'),

    path('usertest/', UserTestProgressAPIView.as_view(), name='admin_usertest'),
    path('usertest/<int:progress_id>/', UserTestProgressAPIView.as_view(), name='admin_usertest_detail'),

    path('option/', OptionsAPIView.as_view(), name='admin_option'),
    path('option/<int:option_id>/', OptionsAPIView.as_view(), name='admin_option_detail'),

    path('testquestion/', TestsQuestionsAPIView.as_view(), name='admin_testquestion'),

    path('optionquestion/', QuestionOptionsAPIView.as_view(), name='admin_optionquestion'),

    path('materials/', MaterialsAPIView.as_view(), name='admin_materials'),
    path('materials/<int:material_id>/', MaterialsAPIView.as_view(), name='admin_materials'),

    path('usermodules/', MaterialsAPIView.as_view(), name='admin_usermodules'),
    path('usermodules/<int:link_id>/', MaterialsAPIView.as_view(), name='admin_usermodules'),

]
