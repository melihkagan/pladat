
from mainapp.models import Student, Job, Employer, Skill, StudentSkill, JobSkill, Application, Setting, Notification

def navbar_skill(request):
    all_skills = []
    skills = Skill.objects.values_list()
    print(all_skills)
    for i in range(len(skills)):
        all_skills.append(skills[i][1])
    context = {
        "skills_database": all_skills
    }
    return context