from mainapp.models import Student, Job, Employer, Skill, StudentSkill, JobSkill, Application


def get_skill_rate_zipped_student(student):
    
    students_skill = StudentSkill.objects.filter(student_id=student.id)
    students_skill_list = []
    students_rate_list = []
    for item in students_skill:
        students_skill_list.append(Skill.objects.get(id=item.skill_id).skill)
        students_rate_list.append(item.rate)
    students_skill_total = zip(students_skill_list,students_rate_list)
    return students_skill_total

def get_skill_rate_zipped_job(job):

    jobs_skill = JobSkill.objects.filter(job_id=job.id)
    jobs_skill_list = []
    jobs_rate_list = []
    for item in jobs_skill:
        jobs_skill_list.append(Skill.objects.get(id=item.skill_id).skill)
        jobs_rate_list.append(item.rate)
    jobs_skill_total = zip(jobs_skill_list,jobs_rate_list)
    return jobs_skill_total