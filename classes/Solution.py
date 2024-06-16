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
        self.rank = -1

    def set_fitness(self, fitness_value):
        self.fitness = fitness_value
        self.is_changed = True

    def set_duration(self, duration):
        self.duration = duration
        self.is_changed = True

    def set_cost(self, cost):
        self.cost = cost
        self.is_changed = True

    # def __str__(self):
    #     representation = "fitness: " + str(self.fitness) + "\n"
    #     for hour, assignments in self.schedule.items():
    #         representation += f"{hour}"
    #         for resource, task in assignments:
    #             representation += f" {resource}-{task}"
    #         representation += "\n"
    #     return representation

    def __str__(self):
        return f"rank: {self.rank} duration: {self.duration} cost: {self.cost} crowding_distance: {self.crowding_distance}"

    def save_to_file(self, file_name):
        with open("./problem_files/solutions/" + file_name + '.best_known_solution_duration', 'w') as file:
            file.write("Hour 	 Resource assignments (resource ID - task ID)\n")
            for hour, assignments in self.schedule.items():
                file.write(f"{hour}")
                for resource, task in assignments:
                    file.write(f" {resource}-{task}")
                file.write("\n")

    def read_from_file(self, file_path):
        with open(file_path, 'r') as file:
            lines = file.readlines()
            for line in lines[1:]:
                split_line = line.split()
                hour = int(split_line[0])
                assignments = split_line[1:]
                self.schedule[hour] = [(int(pair.split('-')[0]), int(pair.split('-')[1])) for pair in assignments]