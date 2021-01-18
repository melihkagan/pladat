from django.contrib import admin
from mainapp.models import Student, Job, Employer, Skill, StudentSkill, JobSkill, Application, Setting, Notification
from django.db import models

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

def userfilter():
    id_list= []
    obj = Setting.objects.all().filter(not_news = True)
    for o in obj:
        id_list.append(o.user_id)
    return id_list

class send_news(models.Model):
    title = models.CharField(max_length=250)
    description = models.CharField(max_length=1000)
    link = models.CharField(max_length=250)
    publish_time = models.DateTimeField(auto_now_add=True, blank=True)

class sendnews(admin.ModelAdmin):
    model = send_news
    fields = ['title', 'description', 'link']
    def save_model(self, request, obj, form, change):
        id_list = userfilter()
        title = form.cleaned_data['title']
        desp = form.cleaned_data['description']
        link = form.cleaned_data['link']
        for id in id_list:
            Notification(user_id = id, title= title, description = desp, link = link).save()
        super(sendnews, self).save_model(request, obj, form, change)

admin.site.register(send_news,sendnews)