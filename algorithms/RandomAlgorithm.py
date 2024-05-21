from abstractClasses.Algorithm import Algorithm
from Solution import Solution
from random import randint, choice


class RandomAlgorithm(Algorithm):

    def __init__(self, instance):
        super().__init__(instance)

    def initialize(self, population_size):
        self.population = [self.random_solution() for _ in range(population_size)]

    def random_solution(self):
        solution = Solution()

        # Sort tasks by the number of predecessor IDs in ascending order
        sorted_tasks = sorted(self.instance.tasks.values(), key=lambda x: len(x.predecessor_ids))

        # Dictionary to store the end times for tasks
        task_end_times = {}

        # Dictionary to store resource availability times
        resource_availability = {res_id: 0 for res_id in self.instance.resources.keys()}

        for task in sorted_tasks:
            if not task.predecessor_ids:  # No predecessors
                earliest_start = 0
            else:  # Calculate the earliest start time considering predecessors
                earliest_start = max(task_end_times.get(pred, 0) for pred in task.predecessor_ids)

            # Find the earliest time a resource is available after the task's earliest start time
            earliest_available_time = float('inf')
            selected_resource = None

            for res_id, res in self.instance.resources.items():
                if res.skills[task.skills_required[0]] >= task.skills_required[1]:
                    available_time = max(earliest_start, resource_availability[res_id])
                    if available_time < earliest_available_time:
                        earliest_available_time = available_time
                        selected_resource = res_id

            if selected_resource is not None:

                # Assign the task to the selected resource at the earliest available time
                hour = earliest_available_time
                if hour not in solution.schedule:
                    solution.schedule[hour] = []
                solution.schedule[hour].append((selected_resource, task.task_id))

                # Update the end time for the task and the availability time for the resource
                task_end_time = hour + task.duration
                task_end_times[task.task_id] = task_end_time
                resource_availability[selected_resource] = task_end_time

        solution.is_changed = True
        return solution
