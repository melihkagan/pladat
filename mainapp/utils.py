from mainapp.models import Student, Job, Employer, Skill, StudentSkill, JobSkill, Application


def get_skill_rate_zipped_student(student):
    
    students_skill = StudentSkill.objects.filter(student_id=student.id)
    students_skill_list = []
    students_rate_list = []
    for item in students_skill:
        students_skill_list.append(Skill.objects.get(id=item.skill_id).skill)
        students_rate_list.append(item.rate)
    students_skill_total = zip(students_skill_list, students_rate_list)
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


def match(student):
    def get_point(skill, studentskill, unit):
        dif = studentskill.rate - skill.rate

        if dif < 0:
            point = (10 + dif)
        else:
            point = 10

        point = (point * unit * skill.type) / 10

        return point

    def compute_unit(skills):
        sum = 0
        for skill in skills:
            sum += skill.type
        return 100 / sum

    # highest 5, high 4, medium 3, low 2, lowest 1

    def matching(student, job):
        jobskills = JobSkill.objects.filter(job=job)

        if jobskills.count() == 0:
            return 0

        unit = compute_unit(jobskills)

        point = 0
        for skill in jobskills:
            if StudentSkill.objects.filter(student=student, skill=skill.skill).count() == 1:
                point += get_point(skill, StudentSkill.objects.filter(student=student, skill=skill.skill)[0], unit)

        return point

    # take second element for sort
    def takeSecond(elem):
        return elem[1]

    def match_all_jobs(student):
        jobs = Job.objects.all()
        points = []
        for job in jobs:
            points.append(matching(student, job))

        ids = list(range(0, len(jobs)))
        points_ids = list(zip(ids, points))
        points_ids.sort(key=takeSecond, reverse=True)
        return points_ids

    point = match_all_jobs(student)
    return point

