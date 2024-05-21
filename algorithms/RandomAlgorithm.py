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

        # Sort tasks by the number of predecessor IDs in descending order
        sorted_tasks = sorted(self.instance.tasks.values(), key=lambda x: len(x.predecessor_ids))

        # Dictionary to store start times for tasks
        task_start_times = {}

        for task in sorted_tasks:

            hours = solution.schedule.keys()
            valid_resources = [
                res_id for res_id, res in self.instance.resources.items()
                if res.skills[task.skills_required[0]] >= task.skills_required[
                    1] and (len(hours) == 0 or res.is_busy_until <= max(hours))
            ]
            if valid_resources:
                resource_id = choice(valid_resources)
                self.instance.resources[resource_id].is_busy_until = max(hours) + task.duration if hours else task.duration
                hour = 1 if not hours else max(hours) + 1

                if hour not in solution.schedule:
                    solution.schedule[hour] = []
                solution.schedule[hour].append((resource_id, task.task_id))
                task_start_times[task.task_id] = hour

        solution.is_changed = True
        return solution
