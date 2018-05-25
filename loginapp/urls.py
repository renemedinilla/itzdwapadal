from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('login', views.login, name='login'),
    path('login/authorized', views.authorized, name='authorized'),
    path('graphcall', views.graphcall, name='graphcall'),
]