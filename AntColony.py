import random
from collections import defaultdict
from Instance import Instance
from Task import Task
from Resource import Resource
from Validator import validate_solution

class Solution:
    def __init__(self):
        self.schedule = defaultdict(list)  # key is time, value is list of (resource, task)

class AntColonyOptimizer:
    def __init__(self, instance, num_ants, num_iterations, alpha, beta, evaporation_rate):
        self.instance = instance
        self.num_ants = num_ants
        self.num_iterations = num_iterations
        self.alpha = alpha
        self.beta = beta
        self.evaporation_rate = evaporation_rate
        self.pheromones = self.initialize_pheromones()

    def initialize_pheromones(self):
        pheromones = {}
        for task in self.instance.tasks.values():
            pheromones[task.task_id] = {}
            for next_task in self.instance.tasks.values():
                if next_task.task_id != task.task_id:
                    pheromones[task.task_id][next_task.task_id] = 1.0  # Initial pheromone level
        return pheromones

    def run(self):
        best_solution = None
        best_fitness = float('inf')

        for iteration in range(self.num_iterations):
            solutions = self.construct_solutions()
            self.update_pheromones(solutions)
            for solution in solutions:
                fitness = self.fitness(solution)
                if fitness < best_fitness:
                    best_fitness = fitness
                    best_solution = solution
            print(f"Iteration {iteration}: Best solution fitness = {best_fitness}")

        return best_solution

    def construct_solutions(self):
        solutions = []
        for _ in range(self.num_ants):
            solution = self.construct_solution()
            if solution is not None:
                solutions.append(solution)
        return solutions

    def construct_solution(self):
        solution = Solution()
        tasks_to_schedule = list(self.instance.tasks.values())
        scheduled_tasks = set()
        resource_availability = {r.resource_id: 0 for r in self.instance.resources.values()}

        while tasks_to_schedule:
            task, resource = self.select_task_and_resource(tasks_to_schedule, scheduled_tasks)
            # for only duration (without cost) much better is previous solution
            # which uses select_next_task and select_task_resource separetly
            # this one returns much worse solutions than random for only duration
            if task is None or resource is None:
                return None

            task_start_times = {}
            for hour, assignments in solution.schedule.items():
                for _, task_id in assignments:
                    task_start_times[task_id] = hour

            predecessor_end_times = [task_start_times[p] + self.instance.tasks[p].duration for p in task.predecessor_ids]
            start_time = max(resource_availability[resource.resource_id], max(predecessor_end_times, default=0)+1)

            solution.schedule[start_time].append((resource.resource_id, task.task_id))
            resource_availability[resource.resource_id] = start_time + task.duration
            scheduled_tasks.add(task.task_id)
            tasks_to_schedule.remove(task)

        return solution

    def select_next_task(self, tasks, scheduled_tasks):
        valid_tasks = []

        for task in tasks:
            if all(pred in scheduled_tasks for pred in task.predecessor_ids):
                valid_tasks.append(task)

        if not valid_tasks:
            return None

        pheromone_levels = []
        heuristics = []

        for task in valid_tasks:
            pheromone = sum(self.pheromones[task.task_id].values())
            heuristic = self.calculate_heuristic(task)
            pheromone_levels.append(pheromone ** self.alpha)
            heuristics.append(heuristic ** self.beta)

        probabilities = [pheromone * heuristic for pheromone, heuristic in zip(pheromone_levels, heuristics)]
        total_probability = sum(probabilities)
        if total_probability == 0:
            probabilities = [1 / len(probabilities) for _ in probabilities]
        else:
            probabilities = [p / total_probability for p in probabilities]
        return random.choices(valid_tasks, probabilities)[0]

    def calculate_heuristic(self, task):
        return 1.0 / task.duration

    def select_resource_for_task(self, task, resource_availability):
        available_resources = [r for r in self.instance.resources.values() if self.is_resource_suitable(r, task)]
        if not available_resources:
            return None
        return min(available_resources, key=lambda r: resource_availability[r.resource_id])

    def select_task_and_resource(self, tasks, scheduled_tasks):
        best_task = None
        best_resource = None
        best_score = float('inf')

        for task in tasks:
            if all(pred in scheduled_tasks for pred in task.predecessor_ids):
                for resource in self.instance.resources.values():
                    if self.is_resource_suitable(resource, task):
                        
                        score = self.calculate_score(task, resource)

                        if score < best_score:
                            best_score = score
                            best_task = task
                            best_resource = resource

        return best_task, best_resource

    def calculate_score(self, task, resource):
        duration_factor = task.duration
        cost_factor = resource.salary

        return duration_factor * cost_factor

    def is_resource_suitable(self, resource, task):
        skill, level = task.skills_required
        if resource.skills[skill] < level:
            return False
        return True

    def update_pheromones(self, solutions):
        for task_id, pheromone_levels in self.pheromones.items():
            for next_task_id in pheromone_levels.keys():
                self.pheromones[task_id][next_task_id] *= (1 - self.evaporation_rate)

        for solution in solutions:
            for time in solution.schedule.keys():
                tasks_at_time = solution.schedule[time]
                for i in range(len(tasks_at_time) - 1):
                    current_task_id = tasks_at_time[i][1]
                    next_task_id = tasks_at_time[i+1][1]
                    self.pheromones[current_task_id][next_task_id] += 1.0 / self.fitness(solution)

    def fitness(self, solution):
        duration = self.duration(solution)
        cost = self.cost(solution)
        return duration + cost

    def cost(self, solution):
        total_cost = 0
        for time, tasks in solution.schedule.items():
            for resource_id, task_id in tasks:
                total_cost += self.instance.resources[resource_id].salary * self.instance.tasks[task_id].duration
        return total_cost

    def duration(self, solution):
        if not solution.schedule:
            return 0
        return max(solution.schedule.keys())