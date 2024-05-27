from collections import OrderedDict


class Solution():
    def __init__(self):
        self.schedule = OrderedDict()
        self.fitness = 0
        self.is_changed = True
        # multiobjective
        self.duration = 0
        self.cost = 0
        self.crowding_distance = 0

    def set_fitness(self, fitness_value):
        self.fitness = fitness_value
        self.is_changed = True

    def set_duration(self, duration):
        self.duration = duration
        self.is_changed = True

    def set_cost(self, cost):
        self.cost = cost
        self.is_changed = True

    def __str__(self):
        representation = "fitness: " + str(self.fitness) + "\n"
        for hour, assignments in self.schedule.items():
            representation += f"{hour}"
            for resource, task in assignments:
                representation += f" {resource}-{task}"
            representation += "\n"
        return representation

    def save_to_file(self, file_name):
        with open("./solutions/"+file_name+'.sol', 'w') as file:
            file.write("Hour 	 Resource assignments (resource ID - task ID)\n")
            for hour, assignments in self.schedule.items():
                file.write(f"{hour}")
                for resource, task in assignments:
                    file.write(f" {resource}-{task}")
                file.write("\n")