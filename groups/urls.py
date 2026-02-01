from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('browse/', views.browse_groups, name='browse_groups'),
    path('create/', views.create_group, name='create_group'),
    path('group/<int:pk>/', views.group_detail, name='group_detail'),
    path('group/<int:pk>/join/', views.join_group, name='join_group'),
    path('group/<int:pk>/leave/', views.leave_group, name='leave_group'),
    path('group/<int:pk>/resource/add/', views.add_resource, name='add_resource'),
    path('group/<int:pk>/message/send/', views.send_message, name='send_message'),
    path('group/<int:pk>/messages/', views.get_messages, name='get_messages'),
    path('group/<int:pk>/session/add/', views.add_session, name='add_session'),
]