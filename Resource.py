class Resource:
    """
    Class to store the resources of the instance.
    Attributes:
        resource_id -- ID of the resource
        salary -- salary of the resource
        skills -- tuple with the values indicating the skills of the resource
            example: (-1,0,3) means that Q0: isn't in the list, Q1: 0, Q2: 3
    """
    def __init__(self, resource_id, salary, skills_number, skills):
        self.resource_id = int(resource_id)
        self.salary = float(salary)
        self.skills = self.parse_skills(skills, skills_number)
        self.is_busy_until = 0

    def __str__(self):
        return f"Resource {self.resource_id} with salary {self.salary} and skills {self.skills}"


    def parse_skills(self, skills,skills_number):
        skills_list = [-1] * skills_number
        x = iter(skills.split())

        for index,value in zip(x,x):
            skills_list[int(index[1])] = int(value)

        return tuple(skills_list)