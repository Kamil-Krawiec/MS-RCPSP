def parse_skills(skills,skills_number):
    skills_list = [-1] * skills_number
    x = iter(skills.split())

    for index,value in zip(x,x):
        skills_list[int(index[1])] = int(value)

    return tuple(skills_list)