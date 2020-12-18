from django import forms

class SkillForm(forms.Form):
    skill = forms.CharField(initial='skill', max_length=100)


