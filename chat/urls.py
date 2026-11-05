from django.urls import path

from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('dashboard/', views.home, name='dashboard'),
    path('rooms/<slug:slug>/', views.room, name='room'),
]
