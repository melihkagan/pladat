from django.urls import path, include

from . import views

urlpatterns = [
    path('landing/', views.landing, name='landing'),
    path('employer/', views.employer, name='employer'),
    path('profile/<username>/', views.view_self_profile, name='view_self_profile'),
    path('add/', views.add_skill, name='add_skill'),
    path('signup/', views.signup, name='signup'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('', views.index, name = 'index'),
]