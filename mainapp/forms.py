import unicodedata

from django import forms
from . import models
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

class SkillForm(forms.Form):
    skill = forms.CharField(initial='skill', max_length=100, required=True)

class JobskillForm(forms.Form):
    skill = forms.CharField(initial='skill', max_length=100, required=True)
    type = forms.IntegerField(initial='type', required=True)

class JobForm(forms.Form):
    title = forms.CharField(initial='title', max_length=200)
    description = forms.CharField(initial='description', max_length=600)
    duedate = forms.DateField(initial='duedate')

class SignupForm(UserCreationForm):
    email = forms.CharField( widget=forms.TextInput(), max_length=100, required=True)

    USERTYPES = (('1', 'Student'), ('2', 'Employer'))
    usertype = forms.CharField(widget=forms.Select(choices=USERTYPES), required=True)
    name = forms.CharField( widget=forms.TextInput(), max_length=100, required=True)
    surname = forms.CharField( widget=forms.TextInput(), max_length=100, required=True)



