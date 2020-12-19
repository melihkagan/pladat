from django.urls import path, include

from . import views

urlpatterns = [
    path('landing/', views.landing, name='landing'),
    path('employer/', views.employer, name='employer'),
    path('see-details/', views.see_details, name='see_details'),
    path('<int:userid>/', views.view_self_profile, name='view_self_profile'),
    path('<int:userid>/add/', views.add_job, name='add_job'),
    path('signup/', views.signup, name='signup'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('', views.index, name = 'index'),
]
