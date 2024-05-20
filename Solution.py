from collections import OrderedDict

class Solution():
    def __init__(self):
        self.schedule = OrderedDict()
        self.fitness = 0
        self.is_changed = True

    def set_fitness(self, fitness_value):
        self.fitness = fitness_value
        self.is_changed = True
