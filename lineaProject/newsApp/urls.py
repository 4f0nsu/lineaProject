from django.urls import path
from . import views

app_name = 'news'

urlpatterns = [
    path('', views.news_index, name='news_index'),
    path('search/', views.news_search, name='news_search'),

]
