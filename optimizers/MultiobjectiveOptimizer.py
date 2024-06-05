import random

from Solution import Solution
from abstractClasses.Optimizer import Optimizer


class MultiobjectiveOptimizer(Optimizer):

    def __init__(self, algorithm):
        super().__init__(algorithm)

    def optimize(self):
        for generation in range(Optimizer.NUM_GENERATIONS):
            self.evaluate()
            self.non_dominated_sort()

            new_population = []
            while len(new_population) < Optimizer.POPULATION_SIZE:
                parent1 = self.selection()
                parent2 = self.selection()
                if random.random() < Optimizer.CROSSOVER_PROBABILITY:
                    child1 = self.crossover(parent1, parent2)
                    child2 = self.crossover(parent2, parent1)
                else:
                    child1 = parent1
                    child2 = parent2
                # if random.random() < Optimizer.MUTATION_PROBABILITY:
                #     self.mutation(child1)
                #     self.mutation(child2)
                # else:
                #     child1 = parent1
                #     child2 = parent2
                new_population.append(child1)
                new_population.append(child2)

            self.algorithm.population = new_population
        self.evaluate()

    def non_dominated_sort(self):
        sorted_population = []
        population_grouped_by_front = []
        rest_of_the_population = [sol for sol in self.algorithm.population if sol not in sorted_population]
        rank = 0
        while rest_of_the_population:
            rest_of_the_population = [sol for sol in self.algorithm.population if sol not in sorted_population]

            current_pareto_front = self.pareto_front(rest_of_the_population, rank)
            sorted_population.extend(current_pareto_front)
            population_grouped_by_front.append(current_pareto_front)
            self.calculate_crowding_distance(current_pareto_front)
            rank += 1

    def calculate_crowding_distance(self, pareto_front):
        num_objectives = 2  # Assuming there are two objectives: duration and cost
        for solution in pareto_front:
            solution.crowding_distance = 0

        for objective_index in range(num_objectives):
            # Sort the Pareto front based on the current objective
            pareto_front.sort(key=lambda x: x.duration if objective_index == 0 else x.cost)
            # Assign infinite crowding distance to boundary solutions
            pareto_front[0].crowding_distance = float('inf')
            pareto_front[-1].crowding_distance = float('inf')

            # Calculate crowding distance for interior solutions
            max_value = max(
                getattr(solution, 'duration' if objective_index == 0 else 'cost') for solution in pareto_front)
            min_value = min(
                getattr(solution, 'duration' if objective_index == 0 else 'cost') for solution in pareto_front)
            range_value = max_value - min_value

            if range_value == 0:
                # All solutions have the same value for this objective, set crowding distance to 0
                continue

            for i in range(1, len(pareto_front) - 1):
                pareto_front[i].crowding_distance += (
                        (getattr(pareto_front[i + 1], 'duration' if objective_index == 0 else 'cost') -
                         getattr(pareto_front[i - 1], 'duration' if objective_index == 0 else 'cost')) / range_value
                )

    def mutation(self, solution):
        pass

    # DHGA crossover proposed by Mehdi Deiranlou and Fariborz Jolai in 2009
    def crossover(self, parent1, parent2):
        child = Solution()

        schedule1 = [(hour, resource, task) for hour, assignments in parent1.schedule.items() for resource, task in
                     assignments]

        schedule2 = [(hour, resource, task) for hour, assignments in parent2.schedule.items() for resource, task in
                     assignments]

        crossover_start_hour = random.choice(schedule1)[0]
        crossover_end_hour = random.choice([x for x in schedule1 if x[0] != crossover_start_hour])[0]

        if crossover_start_hour > crossover_end_hour:
            crossover_start_hour, crossover_end_hour = crossover_end_hour, crossover_start_hour

        first_part = [(x[1], x[2]) for x in schedule1 if crossover_start_hour >= x[0]]
        second_part = [(x[1], x[2]) for x in schedule1 if crossover_end_hour <= x[0]]

        performed_tasks = [x[1] for x in first_part] + [x[1] for x in second_part]

        middle_part = [(x[1], x[2]) for x in schedule2 if x[2] not in performed_tasks]

        child_schedule = first_part + middle_part + second_part

        child.schedule = self.update_schedule(child_schedule)
        child.is_changed = True

        return child

    def update_schedule(self, ordered_list):
        # Dictionary to store the end times for tasks
        task_end_times = {}

        instance = self.algorithm.instance

        # Dictionary to store resource availability times
        resource_availability = {res_id: 0 for res_id in instance.resources.keys()}

        # Dictionary to store the final schedule with hours
        schedule = {}

        for resource, task_id in ordered_list:
            task = instance.tasks[task_id]

            if not task.predecessor_ids:  # No predecessors
                earliest_start = 0
            else:
                # Calculate the earliest start time considering predecessors
                earliest_start = max(task_end_times[pred] for pred in task.predecessor_ids)

            available_time = max(earliest_start, resource_availability[resource])

            # Assign the task to the selected resource at the earliest available time
            if available_time not in schedule:
                schedule[available_time] = []
            schedule[available_time].append((resource, task_id))

            # Update the end time for the task and the availability time for the resource
            task_end_time = available_time + task.duration
            task_end_times[task_id] = task_end_time
            resource_availability[resource] = task_end_time

        # Sort the schedule by hour
        schedule = dict(sorted(schedule.items()))

        return schedule

    # end of crossover

    def selection(self):
        """It means that for two individuals with differing nondominated ranks (different layers),
        the solution with the lower rank (layer) is preferred.
        Otherwise, for two solutions of the same layer,
        the solution placed in the region with a lower concentration of solutions is selected.
        This is the concept of dominated sorting algorithm.
        """
        tournament = random.sample(self.algorithm.population, self.TOURNAMENT_SIZE)
        tournament.sort(key=lambda x: (x.rank, -x.crowding_distance))
        return tournament[0]

    def pareto_front(self, population=None, rank=0):
        population = population if population else self.algorithm.population

        pareto_front = []

        for solution in population:
            is_pareto = True
            for other_solution in population:
                if (solution.duration > other_solution.duration and solution.cost >= other_solution.cost) or \
                        (solution.duration >= other_solution.duration and solution.cost > other_solution.cost):
                    is_pareto = False
                    break
            if is_pareto:
                solution.rank = rank
                pareto_front.append(solution)

        return pareto_front
