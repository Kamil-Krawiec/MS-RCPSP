from abc import ABC, abstractmethod
from Instance import Instance


def execute(solution):
    solution.set_fitness(fitness(solution))


class Algorithm(ABC):

    def __init__(self, instance: Instance):
        self.instance = instance
        self.bestSolution = None
        self.population = []

    @abstractmethod
    def initialize(self, population_size):
        # method to initialize the algorithm
        pass

    def execute(self):
        for solution in filter(lambda sol: sol.is_changed, self.population):
            solution.set_fitness(self.fitness(solution))

    def fitness(self, solution):
        duration = max(solution.schedule.keys())
        cost = 0

        for tasks in solution.schedule.values():
            for resource, task in tasks:
                cost += self.instance.resources[resource].salary * self.instance.tasks[task].duration

        return duration+cost

    def validate_solution(self, solution):
        # method to validate the solution
        pass
