from functions import parse_skills


class Instance:
    """Class to store the instance with tasks and resources.
    Attributes:
        tasks -- dictionary with tasks where key is the ID of the task
        resources -- dictionary with resources where key is the ID of the resource
    """

    def __init__(self, tasks, resources):
        self.tasks = {task.task_id: task for task in tasks}
        self.resources = {resource.resource_id: resource for resource in resources}

    def __str__(self):
        return f"Instance with {len(self.tasks)} tasks and {len(self.resources)} resources"

    def print_tasks(self):
        for task in self.tasks.values():
            print(task)

    def print_resources(self):
        for resource in self.resources.values():
            print(resource)


class Task:
    """Class to store the tasks of the instance.
    Attributes:
        task_id -- ID of the task
        duration -- duration of the task
        skills_required -- tuple with the skills required for the task in the form (index_of_necessary_skill, min_value)
        predecessor_ids -- tuple with the IDs of the tasks that are predecessors of this task
    """

    def __init__(self, task_id, duration, skills_required, predecessor_ids):
        self.task_id = int(task_id)
        self.duration = int(duration)
        self.skills_required = skills_required
        self.predecessor_ids = predecessor_ids

    def __str__(self):
        return f"Task {self.task_id} with duration {self.duration} and skills required " \
               f"{self.skills_required} and predecessors {self.predecessor_ids}"


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
        self.skills = parse_skills(skills, skills_number)

    def __str__(self):
        return f"Resource {self.resource_id} with salary {self.salary} and skills {self.skills}"


def Solution():
    # solution is a list of tuples with (hour started, (resID-TaskID,...))
    pass
