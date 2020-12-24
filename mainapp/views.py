from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, HttpResponseRedirect
from django import forms
from .forms import SkillForm, JobForm, SignupForm
from mainapp.models import Student, Job, Employer, Skill, StudentSkill, JobSkill
# Create your views here.

def landing(request):
    return render(request, 'landing.html')

@login_required
def index(request):
    return render(request, "index.html")

# @login_required
# def employer(request):
#     return render(request, "employer.html")

@login_required
def see_details(request):
    return render(request, "see-details.html")

@login_required
def settings_student(request):
    userid = request.user.id
    student = Student.objects.get(user_id=userid)
    skills_database = []
    skills = Skill.objects.values_list()
    self_skills = StudentSkill.objects.filter(student=student)
    for i in range(len(skills)):
        skills_database.append(skills[i][1])
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = SkillForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            print(form.cleaned_data['skill'])
            print(request.POST['star'])
            skill = Skill.objects.filter(skill=form.cleaned_data['skill'])
            print(skill[0])
            star_int = int(request.POST['star'])
            StudentSkill(student=student, skill=skill[0], rate=star_int).save()
    return render(request, "settings-student.html", {"skills_database": skills_database, "self_skills": self_skills})

@login_required
def settings_employer(request, userid):
    return render(request, "settings-employer.html")

@login_required
def view_self_profile(request, userid):
    # check if the user is student or employer, show according profile page
    if Student.objects.filter(user_id=userid).count()==1:
        student = Student.objects.get(user_id=userid)           
        return render(request, "profile.html", {"student": student} )
    if Employer.objects.filter(user_id=userid).count()==1: 
        employer = Employer.objects.get(user_id=userid)  
        return render(request, "employer.html", {"employer": employer})

@login_required
def add_job(request, userid):
    userid = request.user.id
    username = request.user.username
    employer = Employer.objects.get(user_id=userid)
    skills_database = []
    skills = Skill.objects.values_list()
    for i in range(len(skills)):
        skills_database.append(skills[i][1])
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        print("here")
        if 'job_form' in request.POST:
            print("here")
            form = JobForm(request.POST)
            if form.is_valid():
                print("burada")
                print(form.cleaned_data['title'])
                print(form.cleaned_data['description'])
                print(form.cleaned_data['duedate'])
                title = form.cleaned_data['title']
                description = form.cleaned_data['description']
                duedate = form.cleaned_data['duedate']
                Job(job_title=title, job_description=description, employer=employer, due_date=duedate).save()
        elif 'skill_form' in request.POST:
            print("here")
            form = SkillForm(request.POST)
            # check whether it's valid:
            if form.is_valid():
                print(form.cleaned_data['skill'])
                print(request.POST['star'])
                skill = Skill.objects.filter(skill=form.cleaned_data['skill'])
                print(skill[0])
                star_int = int(request.POST['star'])
                job = Job.objects.filter(employer=employer).last()
                JobSkill(job=job, skill=skill[0], rate=star_int).save()
                job_skills = JobSkill.objects.filter(job=job)
                return render(request, 'addjob.html',
                              {'username': username, "skills_database": skills_database, "job_skills": job_skills})

    # if a GET (or any other method) we'll create a blank form
    return render(request, 'addjob.html', {'username': username, "skills_database": skills_database})

def signup(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            form.save()

            username = User.objects.get(username = form.cleaned_data.get('username'))
            user_mail = form.cleaned_data.get('email')
            username.email = user_mail
            username.save()

            user_name = form.cleaned_data.get('name')
            user_surname = form.cleaned_data.get('surname')
            if(form.cleaned_data.get('usertype') == '1'):
                Student(user_id = username.id, name = user_name, surname = user_surname, e_mail = user_mail).save()
            elif(form.cleaned_data.get('usertype') == '2'):
                Employer(user_id = username.id, name = user_name, surname = user_surname, e_mail = user_mail).save()

            return redirect('index')
    else:
        form = SignupForm()
    return render(request, 'registration/signup.html', {
        'form': form
    })

@login_required
def login(request):
    return redirect('index.html')

