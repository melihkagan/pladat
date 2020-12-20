from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, HttpResponseRedirect
from .forms import SkillForm, JobForm
from mainapp.models import Student, Job, Employer
# Create your views here.

def landing(request):
    return render(request, 'landing.html')

@login_required
def index(request):
    return render(request, "index.html")

@login_required
def employer(request):
    return render(request, "employer.html")

@login_required
def see_details(request):
    return render(request, "see-details.html")

@login_required
def settings_student(request):
    return render(request, "settings-student.html")

@login_required
def settings_employer(request):
    return render(request, "settings-employer.html")

@login_required
def view_self_profile(request, userid):
    userid = request.user.id
    username = request.user.username
    template = "profile.html"
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = SkillForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            print(form.cleaned_data['skill'])
            print(request.POST['star'])
            skill = form.cleaned_data['skill']
            star_int = int(request.POST['star'])
            Student(skill_1=skill, condition_1=star_int).save()

        return render(request, template, {"username": username})
    return render(request, template, {"username": username})

@login_required
def add_job(request, userid):
    userid = request.user.id
    username = request.user.username
    print(username)
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = JobForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            print(form.cleaned_data['title'])
            print(request.POST['description'])
            title = form.cleaned_data['skill']
            description = form.cleaned_data['description']
            Job(job_title=title, job_description=description, employer=Employer).save()

        return render(request, 'addjob.html', {'username': username})
    # if a GET (or any other method) we'll create a blank form
    return render(request, 'addjob.html', {'username': username})

def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('index')
    else:
        form = UserCreationForm()
    return render(request, 'registration/signup.html', {
        'form': form
    })

@login_required
def login(request):
    return redirect('index.html')
