from django.urls import path
from . import views

app_name = 'messages'

urlpatterns = [
    path('', views.inbox, name='inbox'),
    path('users/', views.user_list_view, name='user_list'),
    path('<str:username>/', views.conversation_view, name='conversation'),
]