from django.urls import path, include

from . import views

urlpatterns = [
    path('landing/', views.landing, name='landing'),
    #path('employer/', views.employer, name='employer'),
    path('settings/', views.view_settings, name='settings'),
    path('setting-student/', views.settings_student, name='settings_student'),
    path('setting-employer/', views.settings_employer, name='settings_employer'),
    path('see-details/<int:jobid>/', views.see_details, name='see_details'),
    path('profile/<int:userid>/', views.view_self_profile, name='view_self_profile'), # returns employer and student profile
    path('<int:userid>/add/', views.add_job, name='add_job'),
    path('apply-job/<int:jobid>', views.apply_job, name='apply_job'),
    path('delete-job/<int:jobid>', views.delete_job, name='delete_job'),
    path('update-job/<int:jobid>', views.update_job, name='update_job'),
    path('accept-student/<int:jobid>/<int:studentid>', views.accept_student, name='accept_student'),
    path('decline-student/<int:jobid>/<int:studentid>', views.decline_student, name='decline_student'),
    path('signup/', views.signup, name='signup'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('', views.index, name = 'index'),
    path('notifications/', views.notview.as_view(),  name='notif'),
    path('inbox/', views.mesview.as_view(),  name='mes'),
    path('sendmes/<int:recivid>', views.sendmes , name='sendmes' ),
]
