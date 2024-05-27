from abstractClasses.Optimizer import Optimizer


class MultiobjectiveOptimizer(Optimizer):

    def __init__(self, algorithm):
        super().__init__(algorithm)

    def optimize(self):
        for generation in range(Optimizer.NUM_GENERATIONS):
            # Evaluate the population
            self.evaluate()

    def non_dominated_sort(self):
        sorted_population = []
        population_grouped_by_front = []
        rest_of_the_population = [sol for sol in self.algorithm.population if sol not in sorted_population]

        while rest_of_the_population:
            rest_of_the_population = [sol for sol in self.algorithm.population if sol not in sorted_population]

            sorted_population.extend(self.pareto_front(rest_of_the_population))
            population_grouped_by_front.append(self.pareto_front(rest_of_the_population))

        # Calculate crowding distance for solutions in each Pareto front group
        for front in population_grouped_by_front:
            self.calculate_crowding_distance(front)

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

    def crossover(self, solution, solution2):
        pass

    def selection(self, population):
        pass

    def pareto_front(self, population=None):
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
                pareto_front.append(solution)

        return pareto_front
