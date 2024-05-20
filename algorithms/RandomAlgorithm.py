from abstractClasses.Algorithm import Algorithm
from Solution import Solution
from random import randint, choice


class RandomAlgorithm(Algorithm):

    def __init__(self, instance):
        super().__init__(instance)

    def initialize(self, population_size):
        self.population = [self.random_solution() for _ in range(population_size)]

    def validate_solution(self, solution):
        pass

    def random_solution(self):
        solution = Solution()

        for hour in range(1, 100):
            num_assignments = randint(0, 5)
            assignments = [(choice(list(self.instance.resources.keys())), choice(list(self.instance.tasks.keys())))
                           for _ in range(num_assignments)]
            solution.schedule[hour] = assignments

        return solution
