from abstractClasses.Optimizer import Optimizer
from Solution import Solution
import random

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
                if(random.random() < Optimizer.CROSSOVER_PROBABILITY):
                    child1,child2 = self.crossover(parent1, parent2)
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

    def crossover(self, parent1, parent2):
        # Multi-Skill Precedence Preserving Crossover (MS-PPX)
        def ms_ppx_crossover(parent_x, parent_y):
            child = Solution()

            # Initialize
            tasks = self.algorithm.instance.tasks
            resources = self.algorithm.instance.resources
            num_tasks = len(tasks)
            selection_vector = [random.randint(0, 1) for _ in range(num_tasks)]

            # Extract gene sequences from both parents
            genes_x = [(hour, resource, task) for hour, assignments in parent_x.schedule.items() for resource, task in
                       assignments]
            genes_y = [(hour, resource, task) for hour, assignments in parent_y.schedule.items() for resource, task in
                       assignments]

            scheduled_tasks = set()
            resource_availability = {res_id: 0 for res_id in resources.keys()}
            task_end_times = {}

            # Function to schedule a task ensuring precedence and skill requirements
            def schedule_task(resource, task_id):
                task = tasks[task_id]
                if task_id in scheduled_tasks:
                    return  # Task already scheduled

                # Ensure all predecessors are scheduled
                for pred in task.predecessor_ids:
                    if pred not in scheduled_tasks:
                        if pred in [t for _, _, t in genes_x]:
                            pred_gene = next(g for g in genes_x if g[2] == pred)
                            genes_x.remove(pred_gene)
                            schedule_task(pred_gene[1], pred_gene[2])
                        elif pred in [t for _, _, t in genes_y]:
                            pred_gene = next(g for g in genes_y if g[2] == pred)
                            genes_y.remove(pred_gene)
                            schedule_task(pred_gene[1], pred_gene[2])

                # Determine the earliest start time for the task
                earliest_start = max(
                    task_end_times.get(pred, 0) for pred in task.predecessor_ids) if task.predecessor_ids else 0
                available_time = max(earliest_start, resource_availability[resource])

                # Assign the task to the selected resource at the earliest available time
                if available_time < float('inf'):
                    hour = available_time
                    if hour not in child.schedule:
                        child.schedule[hour] = []
                    child.schedule[hour].append((resource, task.task_id))
                    scheduled_tasks.add(task.task_id)

                    # Update end times and resource availability
                    task_end_time = hour + task.duration
                    task_end_times[task.task_id] = task_end_time
                    resource_availability[resource] = task_end_time

            # Perform crossover
            for i in range(num_tasks):
                if selection_vector[i] == 0:
                    if genes_x:
                        gene = genes_x.pop(0)
                        schedule_task(gene[1], gene[2])
                        genes_y = [g for g in genes_y if g[2] != gene[2]]  # Remove scheduled task from genes_y
                else:
                    if genes_y:
                        gene = genes_y.pop(0)
                        schedule_task(gene[1], gene[2])
                        genes_x = [g for g in genes_x if g[2] != gene[2]]  # Remove scheduled task from genes_x

            # Handle remaining genes
            for gene in genes_x:
                schedule_task(gene[1], gene[2])
            for gene in genes_y:
                schedule_task(gene[1], gene[2])

            # Finalize child solution
            child.is_changed = True
            child.schedule = dict(sorted(child.schedule.items(), key=lambda x: x[0]))

            return child

        # Create two children using MS-PPX
        child1 = ms_ppx_crossover(parent1, parent2)
        child2 = ms_ppx_crossover(parent2, parent1)

        return child1, child2

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
