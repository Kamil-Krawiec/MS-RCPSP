from abstractClasses.Optimizer import Optimizer

class SimpleOptimizer(Optimizer):

        def __init__(self, algorithm):
            super().__init__(algorithm)

        def optimize(self):
            for i in range(Optimizer.NUM_GENERATIONS):
                self.evaluate()

        def mutation(self, solution):
            pass

        def crossover(self, solution, solution2):
            pass

        def selection(self, population):
            pass