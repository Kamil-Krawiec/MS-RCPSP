class Instance:
    """Class to store the instance with tasks and resources.
    Attributes:
        tasks -- dictionary with tasks where key is the ID of the task
        resources -- dictionary with resources where key is the ID of the resource
    """

    def __init__(self, tasks, resources, number_of_relations, number_of_skills):
        self.number_of_relations = number_of_relations
        self.number_of_skills = number_of_skills
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