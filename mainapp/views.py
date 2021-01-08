from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, HttpResponseRedirect
from django import forms
from .forms import SkillForm, JobForm, SignupForm, JobskillForm
from mainapp.models import Student, Job, Employer, Skill, StudentSkill, JobSkill, Application, Setting
from .utils import get_skill_rate_zipped_job, get_skill_rate_zipped_student
# Create your views here.

def landing(request):
    return render(request, 'landing.html')

@login_required
def index(request):
    current_user = request.user
    all_jobs_by_order = Job.objects.all().order_by('-publish_time') # get all published jobs by order
    is_student = (Student.objects.filter(user_id=current_user.id).count()==1) # check if user is student
    if is_student:
        # check student's applied jobs, dont show apply button if already applied.
        student = Student.objects.get(user_id=current_user.id)
        student_applied = Application.objects.filter(student_id=student.id)
        student_applied_job = student_applied.values_list('job_id', flat = True)
    else:
        student_applied_job = []
    return render(request, "index.html",{"jobs": all_jobs_by_order,"is_student": is_student, "student_applied_job": student_applied_job})



@login_required
def see_details(request, jobid):
    current_user = request.user
    job = Job.objects.get(id=jobid) # job to display it's details  
          
    jobs_skill_total = get_skill_rate_zipped_job(job) # Zipping skill-rate and sent them to template 

    # check user is job's owner
    jobs_owner = Employer.objects.get(id = job.employer_id)
    is_jobs_owner =  (current_user.id == jobs_owner.user_id)

    # get applicant students
    applications = Application.objects.filter(job_id = jobid)
    who_applied = []
    for item in applications:
        if item.is_accepted==0: # 0 is waiting, 1 is declined, 2 is accepted
            who_applied.append(Student.objects.get(id = item.student_id))

    # zip everything as one like : applicant students,skills,rates
    students_skill_total_all = []
    for item in who_applied:      
        students_skill_total = get_skill_rate_zipped_student(item)
        students_skill_total_all.append(students_skill_total)      
    students_skill_total_all_zipped = zip(who_applied,students_skill_total_all)

    return render(request, "see-details.html",{"job": job, "jobs_skill_total": jobs_skill_total
                                                , "is_jobs_owner": is_jobs_owner, "students_skill_total_all_zipped": students_skill_total_all_zipped})


@login_required
def settings_student(request):
    userid = request.user.id
    if Employer.objects.filter(user_id=userid).count() == 1:
        return HttpResponse('<b>You are not student</b>')

    student = Student.objects.get(user_id=userid)
    skills_database = []
    skills = Skill.objects.values_list()
    self_skills = StudentSkill.objects.filter(student=student)
    self_skill_array = []
    for skill in self_skills:
        self_skill_array.append(str(skill.skill))
    for i in range(len(skills)):
        skills_database.append(skills[i][1])

    if request.method == 'POST' and 'skillset' in request.POST:
        # create a form instance and populate it with data from the request:
        form = SkillForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            print(form.cleaned_data['skill'])
            # while int(request.POST['star']) == 0:

            print(request.POST['star'])
            skill = Skill.objects.filter(skill=form.cleaned_data['skill'])
            print(skill[0])
            star_int = int(request.POST['star'])
            StudentSkill(student=student, skill=skill[0], rate=star_int).save()
            self_skills = StudentSkill.objects.filter(student=student)
            self_skill_array = []
            for skill in self_skills:
                self_skill_array.append(str(skill.skill))
            return render(request, "settings-student.html", {"skills_database": skills_database, "self_skills": self_skills, "self_skill_array": self_skill_array})
    elif request.method == 'POST' and 'set' in request.POST:
        student.e_mail = request.POST.get('e-mail')
        fullname = request.POST.get('name_surname')
        namearr = fullname.split(' ', 1)
        student.surname = namearr[0]
        student.name = namearr[1]
        student.birth_date = request.POST.get('Date_Of_Birth')
        student.location = request.POST.get('Location')
        student.school_name = request.POST.get('School_name')
        student.department = request.POST.get('department')
        student.cgpa = request.POST.get('cgpa')
        student.start_date = request.POST.get('s_day')
        student.end_date = request.POST.get('e_day')
        student.save()
        if (request.POST.get('not_1')):
            Setting(user_id=userid, not_news=True).save()
        if (request.POST.get('not_2')):
            Setting(user_id=userid, not_matches=True).save()
        if (request.POST.get('not_3')):
            Setting(user_id=userid, not_messages=True).save()

    try:
        curr_set = Setting.objects.get(user_id=userid)
        not1 = curr_set.not_news
        not2 = curr_set.not_matches
        not3 = curr_set.not_messages
        print("here")
    except:
        not1 = False
        not2 = False
        not3 = False
        print("bura")

    context = {
        "skills_database": skills_database, "self_skills": self_skills, "self_skill_array": self_skill_array,
        'username': request.user.username,
        'e_mail': student.e_mail,
        'b_date': student.birth_date,
        'fullname': student.surname + " " + student.name,
        'location': student.location,
        'school': student.school_name,
        'dep': student.department,
        'gpa': student.cgpa,
        's_day': student.start_date,
        'e_day': student.end_date,
        'not1': not1,
        'not2': not2,
        'not3': not3,
    }
    return render(request, "settings-student.html", context)

@login_required
def settings_employer(request):
    current_user = request.user
    userid = current_user.id
    if Student.objects.filter(user_id=userid).count()==1:
        return HttpResponse('<b>You are not employer</b>')
    #emp_setting = Setting.objects.filter(user_id = userid)
    employer = Employer.objects.get(user_id=userid)
    
    if request.method == 'POST':
        employer.e_mail = request.POST.get('e-mail')
        fullname = request.POST.get('name_surname')
        namearr = fullname.split(' ', 1 )
        employer.surname = namearr[0]
        employer.name = namearr[1]
        employer.company_name = request.POST.get('company_name')
        employer.sector = request.POST.get('sector')
        employer.phone = request.POST.get('phone')
        employer.website = request.POST.get('website')
        employer.address = request.POST.get('adress')
        employer.save()
        if request.POST.get('not_1'):
            Setting(user_id = userid, not_news = True ).save()
        if(request.POST.get('not_2')):
            Setting(user_id = userid, not_matches = True ).save()
        if(request.POST.get('not_3')):
            Setting(user_id = userid, not_messages = True ).save()
    
    try:
        curr_set = Setting.objects.get(user_id = userid)
        not1= curr_set.not_news
        not2= curr_set.not_matches
        not3= curr_set.not_messages
    except:
        not1=False
        not2=False
        not3=False
        
    context = {
            'username': current_user.username,
            'e_mail': employer.e_mail,
            'fullname': employer.surname + " " + employer.name,
            'company' : employer.company_name,
            'sector' : employer.sector,
            'phone' : employer.phone,
            'website': employer.website,
            'adress' : employer.address,
            'not1': not1,
            'not2': not2,
            'not3': not3,
        }
    return render(request, "settings-employer.html", context)

@login_required
def view_settings(request):
    userid = request.user.id
    if Student.objects.filter(user_id=userid).count()==1:
        return redirect('settings_student')
    else:
        return redirect('settings_employer')

@login_required
def view_self_profile(request, userid):
    current_user = request.user
    # check if the user is student or employer, show according profile page
    if Student.objects.filter(user_id=userid).count()==1:
        # Zipping skill-rate and sent them to template
        student = Student.objects.get(user_id=userid)           
        students_skill_total = get_skill_rate_zipped_student(student)
        is_users_profile = (current_user.id == student.user_id) # check if profile is user's profile
        # get accepted jobs
        accepted_applications = Application.objects.filter(student_id=student.id, is_accepted=2)
        accepted_applications_jobs = []
        for item in accepted_applications:
            accepted_applications_jobs.append(Job.objects.get(id = item.job_id))
        # get rejected jobs
        declined_applications = Application.objects.filter(student_id=student.id, is_accepted=1)
        declined_applications_jobs = []
        for item in declined_applications:
            declined_applications_jobs.append(Job.objects.get(id = item.job_id))
        return render(request, "profile.html", {"student": student,     
                                                "students_skill_total": students_skill_total,
                                                "accepted_applications_jobs": accepted_applications_jobs,
                                                "declined_applications_jobs": declined_applications_jobs,
                                                "is_users_profile": is_users_profile})

        
    if Employer.objects.filter(user_id=userid).count()==1: 
        employer = Employer.objects.get(user_id=userid)
        # check user is the employer
        employers_job = Job.objects.filter(employer_id = employer.id)  # get selected employer's published jobs
        is_users_profile = (current_user.id == employer.user_id) # check if profile is user's profile
        is_student = (Student.objects.filter(user_id=current_user.id).count()==1) # check if user is student
        if is_student:
            # check student's applied jobs, dont show apply button if already applied.
            student = Student.objects.get(user_id=current_user.id)
            student_applied = Application.objects.filter(student_id=student.id)
            student_applied_job = student_applied.values_list('job_id', flat = True)
        else:
            student_applied_job = [] # to avoid error 
        return render(request, "employer.html", {"employer": employer, "employers_job": employers_job, "is_users_profile": is_users_profile,"is_student": is_student, "student_applied_job": student_applied_job})

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
                job_details = {
                    "title": title,
                    "description": description,
                    "duedate": duedate
                }
                return render(request, 'addjob_skill.html', {'username': username, "skills_database": skills_database, "job_details": job_details})
        elif 'skill_form' in request.POST:
            print("here")
            form = JobskillForm(request.POST)
            # check whether it's valid:
            if form.is_valid():
                print(form.cleaned_data['skill'])
                print(request.POST['star'])
                skill = Skill.objects.filter(skill=form.cleaned_data['skill'])
                print(skill[0])
                star_int = int(request.POST['star'])
                type_int = int(form.cleaned_data['type'])
                job = Job.objects.filter(employer=employer).last()
                JobSkill(job=job, skill=skill[0], rate=star_int, type=type_int).save()
                job_skills = JobSkill.objects.filter(job=job)
                self_skill_array = []
                for skill in job_skills:
                    self_skill_array.append(str(skill.skill))
                return render(request, 'addjob_skill.html', {'username': username, "skills_database": skills_database, "job_details": job, "job_skills": job_skills, "self_skill_array": self_skill_array})

    return render(request, 'addjob.html', {'username': username, "skills_database": skills_database})
@login_required
def apply_job(request,jobid):
    current_user = request.user 
    student = Student.objects.get(user_id=current_user.id)
    Application(job_id=jobid, student_id=student.id).save()
    return index(request)

@login_required
def delete_job(request,jobid):
    Job.objects.get(id=jobid).delete()
    return index(request)

@login_required
def update_job(request,jobid):
    userid = request.user.id
    username = request.user.username
    employer = Employer.objects.get(user_id=userid)
    job = Job.objects.get(id=jobid)
    if( job.employer != employer ):
        return HttpResponse('<b>You cannot update this job</b>')
    skills_database = []
    skills = Skill.objects.values_list()
    for i in range(len(skills)):
        skills_database.append(skills[i][1])
    
    job_skills = JobSkill.objects.filter(job=job)
    self_skill_array = []
    for skill in job_skills:
        self_skill_array.append(str(skill.skill))
    job_details = {
                    "title": job.job_title,
                    "description": job.job_description,
                    "duedate": job.due_date
                }
    context = {
            'jobid' : jobid,
            'username': username, 
            "skills_database": skills_database, 
            "job_details": job_details, 
            "job_skills": job_skills,
            "self_skill_array": self_skill_array,
        }
    if request.method == 'POST':
        if 'skill_form_delete' in request.POST:
            form = JobskillForm(request.POST )
            if form.is_valid():
                skill = Skill.objects.filter(skill=form.cleaned_data['skill'])
                JobSkill.objects.get(job = job, skill=skill[0]).delete()
                job_skills = JobSkill.objects.filter(job=job)
                self_skill_array = []
                for skill in job_skills:
                    self_skill_array.append(str(skill.skill))
                context = {
                    'jobid' : jobid,
                    'username': username, 
                    "skills_database": skills_database, 
                    "job_details": job_details, 
                    "job_skills": job_skills,
                    "self_skill_array": self_skill_array,
                }
                return render(request, 'update_job.html', context)
        elif 'skill_form_update' in request.POST:
            form = JobskillForm(request.POST )
            if form.is_valid():
                skill = Skill.objects.filter(skill=form.cleaned_data['skill'])
                star_int = int(request.POST['star'])
                type_int = int(form.cleaned_data['type'])
                selected = JobSkill.objects.get(job = job, skill=skill[0])
                selected.rate = star_int
                selected.type = type_int
                selected.save()
                job_skills = JobSkill.objects.filter(job=job)
                self_skill_array = []
                for skill in job_skills:
                    self_skill_array.append(str(skill.skill))
                context = {
                    'jobid' : jobid,
                    'username': username, 
                    "skills_database": skills_database, 
                    "job_details": job_details, 
                    "job_skills": job_skills,
                    "self_skill_array": self_skill_array,
                }
                return render(request, 'update_job.html', context)
        elif 'skill_form' in request.POST:
            form = JobskillForm(request.POST )
            if form.is_valid():
                skill = Skill.objects.filter(skill=form.cleaned_data['skill'])
                star_int = int(request.POST['star'])
                type_int = int(form.cleaned_data['type'])
                JobSkill(job=job, skill=skill[0], rate=star_int, type=type_int).save()
                job_skills = JobSkill.objects.filter(job=job)
                self_skill_array = []
                for skill in job_skills:
                    self_skill_array.append(str(skill.skill))
                context = {
                    'jobid' : jobid,
                    'username': username, 
                    "skills_database": skills_database, 
                    "job_details": job_details, 
                    "job_skills": job_skills,
                    "self_skill_array": self_skill_array,
                }
                return render(request, 'update_job.html', context)
        elif 'job_form' in request.POST:
            form = JobForm(request.POST)
            if form.is_valid():
                title = form.cleaned_data['title']
                description = form.cleaned_data['description']
                duedate = form.cleaned_data['duedate']
                job.job_title = title
                job.job_description = description
                job.due_date = duedate
                job.save()
                job_skills = JobSkill.objects.filter(job=job)
                self_skill_array = []
                for skill in job_skills:
                    self_skill_array.append(str(skill.skill))
                job_details = {
                    "title": job.job_title,
                    "description": job.job_description,
                    "duedate": job.due_date
                }
                context = {
                    'jobid' : jobid,
                    'username': username, 
                    "skills_database": skills_database, 
                    "job_details": job_details, 
                    "job_skills": job_skills,
                    "self_skill_array": self_skill_array,
                }
                return render(request, 'update_job.html', context)
                
    return render(request, 'update_job.html', context)


@login_required
def accept_student(request,jobid,studentid):
    selected_application = Application.objects.get(job_id=jobid, student_id=studentid)
    selected_application.is_accepted = 2 # accepted 
    selected_application.save()
    return see_details(request,jobid)

@login_required
def decline_student(request,jobid,studentid):
    selected_application = Application.objects.get(job_id=jobid, student_id=studentid) # get current application
    selected_application.is_accepted = 1 # rejected
    selected_application.save()
    return see_details(request,jobid)

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

