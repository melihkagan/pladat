from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView
from django.views.generic.list import ListView
from django.views.generic.edit import FormView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, HttpResponseRedirect
from django import forms
from .forms import SkillForm, UpdateSkillForm, DeleteSkillForm, JobForm, SignupForm, JobskillForm, ImageFormEmployer, ImageFormStudent, SearchForm, SendmesForm
from mainapp.models import Student, Job, Employer, Skill, StudentSkill, JobSkill, Application, Setting, Notification, Message
from .utils import get_skill_rate_zipped_job, get_skill_rate_zipped_student,match_students,match_jobs

import pandas as pd
# Create your views here.

def landing(request):
    return render(request, 'landing.html')

@login_required 
def index(request):
    if request.method == "GET":   
        current_user = request.user
        all_jobs_by_order = Job.objects.all().order_by('-publish_time') # get all published jobs by order
        jobs_employers = []
        for item in all_jobs_by_order:
            jobs_employers.append(Employer.objects.get(id=item.employer_id))
        jobs_and_employers = zip(all_jobs_by_order,jobs_employers)
        is_student = (Student.objects.filter(user_id=current_user.id).count()==1) # check if user is student
        if is_student:
            # check student's applied jobs, dont show apply button if already applied.
            student = Student.objects.get(user_id=current_user.id)
            student_applied = Application.objects.filter(student_id=student.id)
            student_applied_job = student_applied.values_list('job_id', flat = True)
            matched_jobs = []
            for item in match_jobs(student): # matching algorithm
                #print(item)
                if not item[1] == 0.0:
                    matched_jobs.append(Job.objects.get(id=item[0]))
            #print(matched_jobs)
        else:
            student_applied_job = [] # handle error
            matched_jobs = [] # handle error
        return render(request, "index.html",{"jobs": all_jobs_by_order,
                                            "jobs_and_employers":jobs_and_employers,
                                            "is_student": is_student, 
                                            "student_applied_job": student_applied_job,
                                            "matched_jobs": matched_jobs})
    elif request.method == 'POST':
        form = SearchForm(request.POST)
        if form.is_valid():
            searched_skill = Skill.objects.get(skill=form.cleaned_data['searched_skill'])
        current_user = request.user

        searched_jobs = []
        searched = JobSkill.objects.filter(skill_id=searched_skill.id)
        for item in searched:
            searched_jobs.append(Job.objects.get(id=item.job_id))
        
        searched_jobs.sort(key=lambda x: x.publish_time, reverse=True)

        jobs_employers = []
        for item in searched_jobs:
            jobs_employers.append(Employer.objects.get(id=item.employer_id))
        jobs_and_employers = zip(searched_jobs,jobs_employers)
        is_student = (Student.objects.filter(user_id=current_user.id).count()==1) # check if user is student
        if is_student:
            # check student's applied jobs, dont show apply button if already applied.
            student = Student.objects.get(user_id=current_user.id)
            student_applied = Application.objects.filter(student_id=student.id)
            student_applied_job = student_applied.values_list('job_id', flat = True)
            matched_jobs = []
            for item in match_jobs(student): # matching algorithm
                #print(item)
                matched_jobs.append(Job.objects.get(id=item[0]))
            #print(matched_jobs)
        else:
            student_applied_job = [] # handle error
            matched_jobs = [] # handle error
        return render(request, "index.html",{"jobs": searched_jobs,
                                            "jobs_and_employers":jobs_and_employers,
                                            "is_student": is_student, 
                                            "student_applied_job": student_applied_job,
                                            "matched_jobs": matched_jobs})

@login_required
def see_details(request, jobid):
    current_user = request.user
    job = Job.objects.get(id=jobid) # job to display it's details  
          
    jobs_skill_total = get_skill_rate_zipped_job(job) # Zipping skill-rate and sent them to template 

    # check user is job's owner
    jobs_owner = Employer.objects.get(id = job.employer_id)
    is_jobs_owner =  (current_user.id == jobs_owner.user_id)

    # check if user is student
    is_student = (Student.objects.filter(user_id=current_user.id).count()==1) 
    if is_student:
        # check student's applied jobs, dont show apply button if already applied.
        student = Student.objects.get(user_id=current_user.id)
        student_applied = Application.objects.filter(student_id=student.id)
        student_applied_job = student_applied.values_list('job_id', flat = True)
    else:
        student_applied_job = [] # handle error

    # find matching students
    matched_students = []
    if JobSkill.objects.filter(job_id=job.id).count() >= 1:
        for item in match_students(job):
            #print(item)
            if not item[1] == 0.0:
                matched_students.append(Student.objects.get(id=item[0]))
    
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
    

    return render(request, "see-details.html",{"job": job, "jobs_skill_total": jobs_skill_total,  
                                                "is_student": is_student, "student_applied_job": student_applied_job,
                                                "jobs_owner": jobs_owner,
                                               "is_jobs_owner": is_jobs_owner, 
                                                "students_skill_total_all_zipped": students_skill_total_all_zipped,
                                                "matched_students": matched_students})


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
        #print(request.POST)
        # check whether it's valid:
        if form.is_valid():
            #print(form.cleaned_data['skill'])
            # while int(request.POST['star']) == 0:

            #print(request.POST['star'])
            skill = Skill.objects.filter(skill=form.cleaned_data['skill'])
            #print(skill[0])
            star_int = int(request.POST['star'])
            StudentSkill(student=student, skill=skill[0], rate=star_int).save()
            self_skills = StudentSkill.objects.filter(student=student)
            self_skill_array = []
            for skill in self_skills:
                self_skill_array.append(str(skill.skill))
            
            try:
                curr_set = Setting.objects.get(user_id=userid)
                not1 = curr_set.not_news
                not2 = curr_set.not_matches
                not3 = curr_set.not_messages
            except:
                not1 = False
                not2 = False
                not3 = False
            
            form1 = ImageFormStudent()
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
                'img' : student.profile_img,
                'form': form1,
            }
            return render(request, "settings-student.html", context)

    elif request.method == 'POST' and 'delete' in request.POST:
        form = DeleteSkillForm(request.POST)
        if form.is_valid():
            oldskill = Skill.objects.filter(skill=form.cleaned_data['oldskill'])
            StudentSkill.objects.get(student = student, skill=oldskill[0]).delete()
            self_skills = StudentSkill.objects.filter(student=student)
            self_skill_array = []
            for skill in self_skills:
                self_skill_array.append(str(skill.skill))
    
    elif request.method == 'POST' and 'update' in request.POST:
        
        form = UpdateSkillForm(request.POST)
        if form.is_valid():
            oldskill = Skill.objects.filter(skill=form.cleaned_data['oldskill'])
            StudentSkill.objects.get(student = student, skill=oldskill[0]).delete()
            skill = Skill.objects.filter(skill=form.cleaned_data['updateskill'])
            star_int = int(request.POST['updatestar'])
            StudentSkill(student=student, skill=skill[0], rate=star_int).save()
            self_skills = StudentSkill.objects.filter(student=student)
            self_skill_array = []
            for skill in self_skills:
                self_skill_array.append(str(skill.skill))
        
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
        if Setting.objects.filter(user_id=userid).count()==0:
            Setting(user_id = userid, not_news = False, not_matches = False, not_messages = False).save()
        stu_setting = Setting.objects.get(user_id = userid)
        if request.POST.get('not_1'):
            stu_setting.not_news = True
        else:
            stu_setting.not_news = False
        if(request.POST.get('not_2')):
            stu_setting.not_matches = True
        else:
            stu_setting.not_matches = False
        if(request.POST.get('not_3')):
            stu_setting.not_messages = True
        else:
            stu_setting.not_messages = False
        stu_setting.save()
        
        form1 = ImageFormStudent()
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
        'not1': stu_setting.not_news,
        'not2': stu_setting.not_matches,
        'not3': stu_setting.not_messages,
        'img' : student.profile_img,
        'form': form1
        }
        return render(request, "settings-student.html", context)
    
    elif request.method == 'POST' and 'change_img' in request.POST:
        form = ImageFormStudent(request.POST, request.FILES)
        if form.is_valid():
            student.profile_img = form.cleaned_data['profile_img']
            student.save()
            img_obj = student.profile_img
            try:
                curr_set = Setting.objects.get(user_id=userid)
                not1 = curr_set.not_news
                not2 = curr_set.not_matches
                not3 = curr_set.not_messages
            except:
                not1 = False
                not2 = False
                not3 = False

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
                'img' : student.profile_img,
                'form' : form,
                'img_obj': img_obj,
            }
            return render(request, "settings-student.html", context)
            
    
    try:
        curr_set = Setting.objects.get(user_id=userid)
        not1 = curr_set.not_news
        not2 = curr_set.not_matches
        not3 = curr_set.not_messages
    except:
        not1 = False
        not2 = False
        not3 = False
    
    form1 = ImageFormStudent()
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
        'img' : student.profile_img,
        'form': form1,
    }
    return render(request, "settings-student.html", context)

@login_required
def settings_employer(request):
    current_user = request.user
    userid = current_user.id
    if Student.objects.filter(user_id=userid).count()==1:
        return HttpResponse('<b>You are not employer</b>')
    
    employer = Employer.objects.get(user_id=userid)
    
    if request.method == 'POST' and 'change_img' in request.POST:
        form = ImageFormEmployer(request.POST, request.FILES)
        if form.is_valid():
            employer.profile_img = form.cleaned_data['profile_img']
            employer.save()
            img_obj = employer.profile_img
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
                    'img' : employer.profile_img,
                    'form' : form,
                    'img_obj': img_obj,
                }
            return render(request, "settings-employer.html", context)
    
    elif request.method == 'POST':
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
        if Setting.objects.filter(user_id=userid).count()==0:
            Setting(user_id = userid, not_news = False, not_matches = False, not_messages = False).save()
        emp_setting = Setting.objects.get(user_id = userid)
        if request.POST.get('not_1'):
            emp_setting.not_news = True
        else:
            emp_setting.not_news = False
        if(request.POST.get('not_2')):
            emp_setting.not_matches = True
        else:
            emp_setting.not_matches = False
        if(request.POST.get('not_3')):
            emp_setting.not_messages = True
        else:
            emp_setting.not_messages = False
        emp_setting.save()
        form = ImageFormEmployer()
        context = {
            'username': current_user.username,
            'e_mail': employer.e_mail,
            'fullname': employer.surname + " " + employer.name,
            'company' : employer.company_name,
            'sector' : employer.sector,
            'phone' : employer.phone,
            'website': employer.website,
            'adress' : employer.address,
            'not1': emp_setting.not_news,
            'not2': emp_setting.not_matches,
            'not3': emp_setting.not_messages,
            'img' : employer.profile_img,
            'form' : form,
        }
        return render(request, "settings-employer.html", context)
    
    try:
        curr_set = Setting.objects.get(user_id = userid)
        not1= curr_set.not_news
        not2= curr_set.not_matches
        not3= curr_set.not_messages
    except:
        not1=False
        not2=False
        not3=False
    form = ImageFormEmployer()    
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
            'img' : employer.profile_img,
            'form': form,
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
        
        #Multiple Job Adding 
        if request.method == 'POST' and request.FILES['myfile']:
            myfile = request.FILES['myfile']
            df = pd.read_excel(myfile)
            total_jobs = len(df)

            for i in range(total_jobs):
                job_title = str(df['Job_Title'][i])
                job_desc = str(df['Job_Description'][i])
                date = str(df['Due Date'][i])
                date_list = date.split()
                due_date = date_list[0]
                req_deps = str(df['Req_Departments'][i])
                skills = str(df['Skills'][i])
                rates = str(df['Rates'][i])
                priorities = str(df['Priorities'][i])
                skill_list = skills.split(";")
                rate_list = rates.split(";")
                priority_list = priorities.split(";")
                skill_number = len(skill_list)
                Job(job_title=job_title, job_description=job_desc, employer=employer, due_date=due_date, req_departments=req_deps).save()
                for j in range(skill_number):
                    skill = Skill.objects.filter(skill=skill_list[j])
                    job = Job.objects.filter(employer=employer).last()
                    JobSkill(job=job, skill=skill[0], rate=rate_list[j], type=int(priority_list[j])).save()



        
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
        #print("here")
        if 'job_form' in request.POST:
            #print("here")
            form = JobForm(request.POST)
            if form.is_valid():
                #print("burada")
                #print(form.cleaned_data['title'])
                #print(form.cleaned_data['description'])
                #print(form.cleaned_data['duedate'])
                title = form.cleaned_data['title']
                description = form.cleaned_data['description']
                duedate = form.cleaned_data['duedate']
                req = form.cleaned_data['req_departments']
                Job(job_title=title, job_description=description, employer=employer, due_date=duedate, req_departments=req).save()
                job_details = {
                    "title": title,
                    "description": description,
                    "duedate": duedate,
                    "req_dep": req,
                }
                return render(request, 'addjob_skill.html', {'username': username, "skills_database": skills_database, "job_details": job_details})
        elif 'skill_form' in request.POST:
            #print("here")
            form = JobskillForm(request.POST)
            # check whether it's valid:
            if form.is_valid():
                #print(form.cleaned_data['skill'])
                #print(request.POST['star'])
                skill = Skill.objects.filter(skill=form.cleaned_data['skill'])
                #print(skill[0])
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
                    "duedate": job.due_date,
                    "req_dep": job.req_departments,
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
                req = form.cleaned_data['req_departments']
                job.job_title = title
                job.job_description = description
                job.due_date = duedate
                job.req_departments = req
                job.save()
                job_skills = JobSkill.objects.filter(job=job)
                self_skill_array = []
                for skill in job_skills:
                    self_skill_array.append(str(skill.skill))
                job_details = {
                    "title": job.job_title,
                    "description": job.job_description,
                    "duedate": job.due_date,
                    "req_dep": job.req_departments,
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
    userid= request.user.id
    employer = Employer.objects.get(user_id=userid)
    job = Job.objects.get(id=jobid)
    student = Student.objects.get(id = studentid)
    try:
        stusetting = Setting.objects.get(user_id = student.user_id)
        if( stusetting.not_matches ):
            desp = "Congratulations! You have been hired by " + str(employer.company_name) + " to the "
            desp = desp + str(job.job_title) + " position"
            desp = desp + "<br> Contact :" + "<a class=\"text-light\" href=mailto:" + str(employer.e_mail) + "> "+ str(employer.e_mail) + "</a>"
            link = "see-details/"+ str(jobid) + "/" 
            Notification(user_id = student.user_id, title = "New Match!", link=link, description = desp).save()
    except:
        print("there is no setting object")

    try:
        empsetting = Setting.objects.get(user_id = employer.user_id)
        if( empsetting.not_matches ):
            desp = "Congratulations! You hired " + str(student.name) + " " + str(student.surname) + " to the "
            desp = desp + str(job.job_title) + " position"
            desp = desp + "<br> Contact :" + "<a class=\"text-light\" href=mailto:" + str(student.e_mail) + "> "+ str(student.e_mail) + "</a>"
            link = "profile/" + str(student.user_id) + "/"
            Notification(user_id = employer.user_id, title= "New Match!", link=link, description = desp).save()
    except:
        print("there is no setting object")
    
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
            
            link = "settings/"
            desp= """We are happy to see you here. This is your first notification. 
            <a href=\"../settings/\" class=\"text-light\">Click here</a> to change your notifications settings or 
            to do more like changing your profile picture. Don't forget to adjust your profile settings for a better experience. Enjoy ;) """
            Notification(user_id = username.id, title= "Welcome PlaDat!", link=link, description = desp).save()
            return redirect('index')
    else:
        form = SignupForm()
    return render(request, 'registration/signup.html', {
        'form': form
    })

@login_required
def login(request):
    return redirect('index.html')

#@login_required
class notview(ListView):
      model = Notification 
      paginate_by = 3
      context_object_name = 'notif'
      template_name = 'notification.html'
      def get_queryset(self):
          usernots = Notification.objects.filter(user_id =self.request.user.id)
          return usernots.order_by('-publish_time')

class mesview(ListView):
    model = Message
    paginate_by = 4
    context_object_name = 'mes'
    template_name = 'inbox.html'
    def get_queryset(self):
        usermes = Message.objects.filter(reciever = self.request.user.id)
        return usermes.order_by('-created_at')

@login_required
def sendmes(request, recivid):
    form = SendmesForm
    sendto = User.objects.get(id = recivid)
    sendtoname = sendto.username
    if request.method == 'POST':
        form = SendmesForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data['title']
            mes = form.cleaned_data['msg_content']
            name = request.user.username
            Message(sender = request.user.id, reciever=recivid, title=title, msg_content=mes, sender_name = name).save()
            try:
                recivsetting = Setting.objects.get(user_id = recivid)
                if( recivsetting.not_messages ):
                    link = "inbox/"
                    desp= """You have new message, to check your inbox 
                    <a href=\"../inbox/\" class=\"text-light\">Click here</a> """
                    Notification(user_id = recivid, title= "New Message!", link=link, description = desp).save()
            except:
                print("no setting object")
            return redirect('/profile/' + str(recivid) + '/')
    
    return render(request, "sendmes.html", {"form" : form, "sendto" : sendtoname})
    
            
    