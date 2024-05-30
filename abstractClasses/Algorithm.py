from abc import ABC, abstractmethod

from Instance import Instance


class Algorithm(ABC):

    def __init__(self, instance: Instance):
        self.instance = instance
        self.best_solution = None
        self.worst_solution = None
        self.population = []

    @abstractmethod
    def initialize(self, population_size):
        # method to initialize the algorithm
        pass

    def execute(self):
        for solution in filter(lambda sol: sol.is_changed, self.population):
            solution.set_fitness(self.fitness(solution))
            solution.set_duration(self.duration(solution))
            solution.set_cost(self.cost(solution))

        self.best_solution = min(self.population, key=lambda sol: sol.fitness)
        self.worst_solution = max(self.population, key=lambda sol: sol.fitness)

    def fitness(self, solution):
        duration = self.duration(solution)
        cost = self.cost(solution)

        return duration + cost

    def cost(self, solution):
        cost = 0

        for tasks in solution.schedule.values():
            for resource, task in tasks:
                cost += self.instance.resources[resource].salary * self.instance.tasks[task].duration
        return cost

    def duration(self, solution):
        return max(solution.schedule.keys())

    def execute_solution(self, solution):
        solution.set_fitness(self.fitness(solution))

    def validate_solution(self, solution):
        return (self.validate_assignments(solution) and
                self.validate_conflicts(solution) and
                self.validate_skills(solution) and
                self.validate_precedence_relations(solution))

    def validate_assignments(self, solution):
        # Ensure all tasks are assigned to resources
        assigned_tasks = {task_id for assignments in solution.schedule.values() for _, task_id in assignments}
        all_tasks = set(self.instance.tasks.keys())
        return assigned_tasks == all_tasks

    def validate_conflicts(self, solution):
        # Ensure no resource is assigned to more than one task at the same time
        for hour, assignments in solution.schedule.items():
            resources = [resource_id for resource_id, _ in assignments]
            if len(resources) != len(set(resources)):
                return False
        return True

    def validate_skills(self, solution):
        # Ensure resources have the required skills for assigned tasks
        for hour, assignments in solution.schedule.items():
            for resource_id, task_id in assignments:
                resource = self.instance.resources[resource_id]
                task = self.instance.tasks[task_id]
                if not resource.skills[task.skills_required[0]] >= task.skills_required[1]:
                    return False
        return True

    def validate_precedence_relations(self, solution):
        # Ensure all precedence constraints are met
        task_start_times = {}
        for hour, assignments in solution.schedule.items():
            for _, task_id in assignments:
                task_start_times[task_id] = hour

        for task_id, task in self.instance.tasks.items():
            for predecessor_id in task.predecessor_ids:
                if task_start_times.get(predecessor_id, float('inf')) >= task_start_times.get(task_id, -1):
                    return False
        return True
