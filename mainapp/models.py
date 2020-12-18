from django.db import models

class Employer(models.Model):
    username = models.CharField(max_length=100)
    name = models.CharField(max_length=100)
    surname = models.CharField(max_length=100)
    company = models.CharField(max_length=100)
    title = models.CharField(max_length=100)

class Student(models.Model):
    username = models.CharField(max_length=100)
    name = models.CharField(max_length=100)
    surname = models.CharField(max_length=100)
    university = models.CharField(max_length=100)
    skill_1 = models.CharField(max_length=100,default="")
    condition_1 = models.IntegerField(default=0)
    skill_2 = models.CharField(max_length=100,default="")
    condition_2 = models.IntegerField(default=0)
    skill_3 = models.CharField(max_length=100,default="")
    condition_3 = models.IntegerField(default=0)
    skill_4 = models.CharField(max_length=100,default="")
    condition_4 = models.IntegerField(default=0)
    skill_5 = models.CharField(max_length=100,default="")
    condition_5 = models.IntegerField(default=0)

class Job(models.Model):
    employer = models.ForeignKey(Employer, on_delete=models.CASCADE)
    job_title = models.CharField(max_length=100)
    job_description = models.CharField(max_length=100)
    publish_time = models.DateTimeField(auto_now_add=True, blank=True)

    skill_1 = models.CharField(max_length=100,default="")
    condition_1 = models.IntegerField(default=0)
    skill_2 = models.CharField(max_length=100,default="")
    condition_2 = models.IntegerField(default=0)
    skill_3 = models.CharField(max_length=100,default="")
    condition_3 = models.IntegerField(default=0)
    skill_4 = models.CharField(max_length=100,default="")
    condition_4 = models.IntegerField(default=0)
    skill_5 = models.CharField(max_length=100,default="")
    condition_5 = models.IntegerField(default=0)    
class Application(models.Model):
    job = models.ForeignKey(Job, on_delete=models.CASCADE)
    username = models.CharField(max_length=100)
    apply_time = models.DateTimeField(auto_now_add=True, blank=True)
class Skill(models.Model):
    skill = models.CharField(max_length=100)

# Create your models here.
