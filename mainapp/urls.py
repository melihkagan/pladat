from django.urls import path, include

from . import views

urlpatterns = [
    path('landing/', views.landing, name='landing'),
    path('employer/', views.employer, name='employer'),
    path('profile/', views.profile, name='profile'),
    path('signup/', views.signup, name='signup'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('', views.index, name = 'index'),
]