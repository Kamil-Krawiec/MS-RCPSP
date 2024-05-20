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