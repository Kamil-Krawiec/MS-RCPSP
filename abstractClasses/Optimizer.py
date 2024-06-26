from abc import ABC, abstractmethod
from abstractClasses.Algorithm import Algorithm
from classes.Solution import Solution


class Optimizer(ABC):
    POPULATION_SIZE = 500
    NUM_GENERATIONS = 120
    CROSSOVER_PROBABILITY = 0.7
    MUTATION_PROBABILITY = 0.13
    TOURNAMENT_SIZE = 5
    OTHER_MUTATION_PROBABILITY = 0.35

    def __init__(self, algorithm: Algorithm):
        self.algorithm = algorithm

    def initialize(self):
        self.algorithm.initialize(Optimizer.POPULATION_SIZE)

    @abstractmethod
    def optimize(self):
        # method to optimize the model
        pass

    @abstractmethod
    def mutation(self, solution: Solution):
        # method to mutate the solution
        pass

    @abstractmethod
    def crossover(self, solution: Solution, solution2: Solution):
        # method to cross over the solution
        pass

    def selection(self):
        # method to select the best solutions from the population
        pass

    def evaluate(self):
        self.algorithm.execute()

    def get_statistics(self):
        return self.algorithm.worst_solution, self.algorithm.best_solution
