from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('requirements/', views.requirement_list, name='requirement_list'),
    path('requirements/new/', views.requirement_new, name='requirement_new'),
    path('requirements/<int:pk>/', views.requirement_detail, name='requirement_detail'),
]
