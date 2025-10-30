from django.urls import path
from . import views

app_name = 'posts'

urlpatterns = [
    path('', views.FeedView.as_view(), name='feed'),
    path('user/<str:username>/', views.UserPostsView.as_view(), name='user_posts'),
    path('create/', views.PostCreateView.as_view(), name='create'),
    path('<int:pk>/', views.PostDetailView.as_view(), name='detail'),
    path('<int:pk>/like/', views.toggle_like, name='like'),
    path('<int:pk>/comment/', views.add_comment, name='comment'),
    path('<int:pk>/delete/', views.PostDeleteView.as_view(), name='delete'),
]
