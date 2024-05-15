from Classes import Resource, Task


class InstanceReader:
    """Class to read the instance file and create the instances of resources and tasks.
    Attributes:
        path -- path to the instance file
        tasks -- number of tasks in the instance
        resources -- number of resources in the instance
        relations -- number of relations in the instance
        skill_types -- number of skill types in the instance
        resources_objects -- list with the lines ready to be parsed by the make_instances_resources method
        task_objects -- list with the lines ready to be parsed by the make_instances_tasks method

        """

    def __init__(self, path):
        self.path = path
        self.tasks = None
        self.resources = None
        self.relations = None
        self.skill_types = None
        self.resources_objects = []
        self.task_objects = []

    def read(self):
        with open(self.path, 'r') as file:
            while (line := file.readline()) != '':
                if line == "General characteristics:\n":
                    self.tasks, self.resources, self.relations, self.skill_types = [int(file.readline().split(':')[-1])
                                                                                    for _ in range(4)]
                if line.startswith("ResourceID"):
                    resource_line = file.readline()
                    while not resource_line.startswith("=="):
                        resource_obj = resource_line.split(maxsplit=2)
                        self.resources_objects.append(resource_obj)
                        resource_line = file.readline()
                if line.startswith("TaskID"):
                    task_line = file.readline()
                    while not task_line.startswith("=="):
                        task_obj = task_line.split()
                        task_obj[2] = task_obj[2] + task_obj[3]
                        task_obj.pop(3)
                        self.task_objects.append(task_obj)
                        task_line = file.readline()

    def make_instances_resources(self):
        res_list = []
        for resource in self.resources_objects:
            resource_id, salary, skills = resource
            res_list.append(Resource(resource_id, salary, self.skill_types, skills))
        return res_list

    def make_instances_tasks(self):
        task_list = []
        for task in self.task_objects:
            task_id, duration, skill, *pred_ids = task
            skill = int(skill[1]), int(skill[3])
            task_list.append(Task(task_id, duration, skill, tuple(map(int, pred_ids))))
        return task_list
