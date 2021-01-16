import unicodedata

from django import forms
from . import models
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Employer,Student

class SkillForm(forms.Form):
    skill = forms.CharField(initial='skill', max_length=100, required=True)

class JobskillForm(forms.Form):
    skill = forms.CharField(initial='skill', max_length=100, required=True)
    type = forms.IntegerField(initial='type', required=True)

class UpdateSkillForm(forms.Form):
    updateskill = forms.CharField(initial='updateskill', max_length=100, required=True)
    oldskill = forms.CharField(initial='oldskill', max_length=100, required=True)

class DeleteSkillForm(forms.Form):
    oldskill = forms.CharField(initial='oldskill', max_length=100, required=True)
    
class JobForm(forms.Form):
    title = forms.CharField(initial='title', max_length=200)
    description = forms.CharField(initial='description', max_length=600)
    duedate = forms.DateField(initial='duedate')
    req_departments = forms.CharField(initial='req_departments', max_length=200)

class SignupForm(UserCreationForm):
    email = forms.CharField( widget=forms.TextInput(), max_length=100, required=True)

    USERTYPES = (('1', 'Student'), ('2', 'Employer'))
    usertype = forms.CharField(widget=forms.Select(choices=USERTYPES), required=True)
    name = forms.CharField( widget=forms.TextInput(), max_length=100, required=True)
    surname = forms.CharField( widget=forms.TextInput(), max_length=100, required=True)

class ImageFormEmployer(forms.ModelForm):
    class Meta:
        model = Employer
        fields = ('profile_img',)

class ImageFormStudent(forms.ModelForm):
    class Meta:
        model = Student
        fields = ('profile_img',)
