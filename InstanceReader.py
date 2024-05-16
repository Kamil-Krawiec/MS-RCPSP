from Resource import Resource
from Task import Task

class InstanceReader:
    """Class to read the instance file and create the instances of resources and tasks."""

    def __init__(self):
        self.number_of_skills = 0

    def read(self, path):
        resources = []
        tasks = []
        with open(path, 'r') as file:
            while (line := file.readline()) != '':
                if line == "General characteristics:\n":
                    _, _, number_of_relations, self.number_of_skills = [
                        int(file.readline().split(':')[-1]) for _ in range(4)
                    ]
                if line.startswith("ResourceID"):
                    resource_line = file.readline()
                    while not resource_line.startswith("=="):
                        resource = resource_line.split(maxsplit=2)
                        resources.append(resource)
                        resource_line = file.readline()
                if line.startswith("TaskID"):
                    task_line = file.readline()
                    while not task_line.startswith("=="):
                        task = task_line.split()
                        task[2] = task[2] + task[3]
                        task.pop(3)
                        tasks.append(task)
                        task_line = file.readline()
        parsed_resources, parsed_tasks = self.parse_resources(resources), self.parse_tasks(tasks)
        return parsed_resources, parsed_tasks, number_of_relations, self.number_of_skills

    def parse_resources(self, resources):
        parsed_resources = []
        for resource in resources:
            resource_id, salary, skills = resource
            parsed_resources.append(Resource(resource_id, salary, self.number_of_skills, skills))
        return parsed_resources

    def parse_tasks(self, tasks):
        parsed_tasks = []
        for task in tasks:
            task_id, duration, skill, *pred_ids = task
            skill = int(skill[1]), int(skill[3])
            parsed_tasks.append(Task(task_id, duration, skill, tuple(map(int, pred_ids))))
        return parsed_tasks
