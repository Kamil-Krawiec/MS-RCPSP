from algorithms.RandomAlgorithm import RandomAlgorithm


class MultiobjectiveAlgorithm(RandomAlgorithm):
    def __init__(self, instance):
        super().__init__(instance)

    def initialize(self, population_size):
        super().initialize(population_size)

    def execute(self):
        for solution in filter(lambda sol: sol.is_changed, self.population):
            solution.set_duration(self.duration(solution))
            solution.set_cost(self.cost(solution))
