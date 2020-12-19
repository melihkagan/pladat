from django import forms

class SkillForm(forms.Form):
    skill = forms.CharField(initial='skill', max_length=100)

class JobForm(forms.Form):
    title = forms.CharField(initial='title', max_length=200)
    description = forms.CharField(initial='description', max_length=600)