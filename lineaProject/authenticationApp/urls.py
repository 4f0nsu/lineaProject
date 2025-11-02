from django.urls import path
from . import views

urlpatterns = [
    path('sign-up/step1/', views.sign_up_step1, name='sign_up_step1'),
    path('sign-up/verify/', views.sign_up_verify_code, name = "sign_up_verify_code"),
    path('sign_up/step2/', views.sign_up_step2, name="sign_up_step2"),
    path('sign-in/', views.sign_in, name='sign_in'),
    path('logout/', views.user_logout, name='user_logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
]