from django.db import models

class Employer(models.Model):
    user_id = models.IntegerField(default=None)
    e_mail = models.EmailField(default=None)
    name = models.CharField(max_length=100,default=None)
    surname = models.CharField(max_length=100,default=None)
    company_name = models.CharField(max_length=100,default=None,null=True)
    sector = models.CharField(max_length=100,default=None,null=True)
    phone = models.CharField(max_length=13,default=None,null=True)
    website = models.CharField(default="",max_length=100,null=True)
    address = models.CharField(default="",max_length=100,null=True)

    def __str__(self):
        return self.name

class Student(models.Model):
    user_id = models.IntegerField(default=None,null=True)
    name = models.CharField(max_length=100,default=None)
    surname = models.CharField(max_length=100,default=None)
    school_name = models.CharField(max_length=100,default=None,null=True)
    department = models.CharField(max_length=100,default=None,null=True)
    birth_date = models.DateField(null=True, blank=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(default=None,null=True)
    cgpa = models.FloatField(default=0.0,null=True) #gpa
    e_mail = models.EmailField(default=None,null=True)

    def __str__(self):
        return self.name

class Job(models.Model):
    employer = models.ForeignKey(Employer, on_delete=models.CASCADE,default=None) #employer_id
    job_title = models.CharField(max_length=100,default=None)
    job_description = models.CharField(max_length=100,default=None) #description
    publish_time = models.DateTimeField(auto_now_add=True, blank=True)
    due_date = models.DateField(default=None,null=True)
    req_departments = models.CharField(max_length=100,default=None,null=True)

    def __str__(self):
        return self.job_title

class Application(models.Model):
    job = models.ForeignKey(Job, on_delete=models.CASCADE,default=None)
    student = models.ForeignKey(Student, on_delete=models.CASCADE,default=None)
    apply_time = models.DateTimeField(auto_now_add=True, blank=True)

    def __str__(self):
        return self.apply_time 

class Skill(models.Model):
    skill = models.CharField(max_length=100,default=None)

    def __str__(self):
        return self.skill

class JobSkill(models.Model):
    job = models.ForeignKey(Job, on_delete=models.CASCADE,default=None)
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE,default=None)
    rate = models.IntegerField(default=0)    

class StudentSkill(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE,default=None)
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE,default=None)
    rate = models.IntegerField(default=0)

class Setting(models.Model):
    not_news = models.BooleanField(default=False)
    not_messages = models.BooleanField(default=False)
    not_matches = models.BooleanField(default=False)



# Create your models here.
