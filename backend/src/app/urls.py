
from django.urls import path, include
from app import views

app_name = 'app'
urlpatterns = [
    path('article/', views.ArticleAPIView.as_view(), name='list'),
]
