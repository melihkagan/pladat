from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('employer', views.employer, name='employer'),
    path('profile', views.profile, name='profile'),
]