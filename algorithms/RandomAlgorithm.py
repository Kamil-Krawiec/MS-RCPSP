from abstractClasses.Algorithm import Algorithm
from classes.Solution import Solution
from random import shuffle


class RandomAlgorithm(Algorithm):

    def __init__(self, instance):
        super().__init__(instance)

    def initialize(self, population_size):
        while len(self.population) < population_size:
            solution = self.random_solution()
            if self.validate_solution(solution):
                self.population.append(solution)

    def random_solution(self):
        solution = Solution()

        # Shuffle tasks to introduce randomness
        tasks = list(self.instance.tasks.values())
        shuffle(tasks)

        # Dictionary to store the end times for tasks
        task_end_times = {}

        # Dictionary to store resource availability times
        resource_availability = {res_id: 0 for res_id in self.instance.resources.keys()}

        while tasks:
            task = tasks.pop(0)

            if not task.predecessor_ids:  # No predecessors
                earliest_start = 0
            else:
                # Check if all predecessors have been scheduled
                unscheduled_predecessors = [pred for pred in task.predecessor_ids if pred not in task_end_times]
                if unscheduled_predecessors:
                    # Push the current task back and schedule predecessors first
                    tasks.append(task)
                    shuffle(tasks)  # Shuffle tasks to introduce randomness in task scheduling
                    continue  # Skip scheduling the current task now

                # Calculate the earliest start time considering predecessors
                earliest_start = max(task_end_times[pred] for pred in task.predecessor_ids)

            # Find all resources that can perform the task
            valid_resources = [
                res_id for res_id, res in self.instance.resources.items()
                if res.skills[task.skills_required[0]] >= task.skills_required[1]
            ]

            # Shuffle the valid resources to introduce randomness
            shuffle(valid_resources)

            for res_id in valid_resources:
                available_time = max(earliest_start, resource_availability[res_id])
                if available_time < float('inf'):
                    selected_resource = res_id
                    earliest_available_time = available_time
                    break

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
        solution.schedule = dict(sorted(solution.schedule.items(), key=lambda x: x[0]))

        return solution
