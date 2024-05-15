from functions import parse_skills


class Instance:
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
    # Skill required is a tuple with (index_of_necessary_skill, min_value)
    def __init__(self, task_id, duration, skills_required, predecessor_ids):
        self.task_id = int(task_id)
        self.duration = int(duration)
        self.skills_required = skills_required
        self.predecessor_ids = predecessor_ids

    def __str__(self):
        return f"Task {self.task_id} with duration {self.duration} and skills required " \
               f"{self.skills_required} and predecessors {self.predecessor_ids}"


class Resource:
    def __init__(self, resource_id, salary, skills_number, skills):
        self.resource_id = int(resource_id)
        self.salary = float(salary)
        self.skills = parse_skills(skills, skills_number)

    def __str__(self):
        return f"Resource {self.resource_id} with salary {self.salary} and skills {self.skills}"


def Solution():
    # solution is a list of tuples with (hour started, (resID-TaskID,...))
    pass

