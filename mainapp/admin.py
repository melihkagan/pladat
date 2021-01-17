from django.contrib import admin
from mainapp.models import Student, Job, Employer, Skill, StudentSkill, JobSkill, Application, Setting, Notification

# Register your models here.
admin.site.register(Student)
admin.site.register(Job)
admin.site.register(Employer)
admin.site.register(Skill)
admin.site.register(StudentSkill)
admin.site.register(JobSkill)
admin.site.register(Application)
admin.site.register(Setting)
admin.site.register(Notification)

