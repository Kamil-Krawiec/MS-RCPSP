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
                    # child1 = self.crossover(parent1, parent2)
                    # child2 = self.crossover(parent2, parent1)
                    child1 = self.PMXCrossover(parent1, parent2)
                    child2 = self.PMXCrossover(parent2, parent1)
                else:
                    child1 = parent1
                    child2 = parent2

                if random.random() < Optimizer.MUTATION_PROBABILITY:
                    # self.mutationSwap(child1)
                    # self.mutationSwap(child2)

                    # self.mutation(child1)
                    # self.mutation(child2)

                    self.mutationTheCheapest(child1)
                    self.mutationTheCheapest(child2)
                else:
                    child1 = parent1
                    child2 = parent2
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
        num_objectives = 2
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

    # Conflict Avoidance Mutation (CAM) proposed by Pawel B. Myszkowski, Marek E. Skowronski in 2013 =================================================================
    def mutation(self, solution):
        instance = self.algorithm.instance

        # Create a copy of resource availability based on the current schedule
        resource_availability = {res_id: 0 for res_id in instance.resources.keys()}
        for hour, assignments in solution.schedule.items():
            for resource, task_id in assignments:
                task = instance.tasks[task_id]
                resource_availability[resource] = max(resource_availability[resource], hour + task.duration)

        # Get the list of tasks for each resource
        resource_task_mapping = {}
        for hour, assignments in solution.schedule.items():
            for resource, task_id in assignments:
                if resource not in resource_task_mapping:
                    resource_task_mapping[resource] = []
                resource_task_mapping[resource].append((hour, task_id))

        ordered_list = []

        # Process each resource's task list to find conflicts
        for resource, tasks in resource_task_mapping.items():
            # Sort tasks by their start times
            tasks.sort(key=lambda x: x[0])

            # Identify pairs of assignments with conflicts
            for i in range(len(tasks) - 1):
                hour1, task_id1 = tasks[i]
                hour2, task_id2 = tasks[i + 1]
                task1 = instance.tasks[task_id1]
                task2 = instance.tasks[task_id2]

                finish_time1 = hour1 + task1.duration

                # If there is a conflict between task1 and task2
                if hour2 - finish_time1 == 0:
                    # Choose the task with more capable resources to be reassigned
                    capable_resources1 = [res_id for res_id, res in instance.resources.items()
                                          if res.skills[task1.skills_required[0]] >= task1.skills_required[1]]
                    capable_resources2 = [res_id for res_id, res in instance.resources.items()
                                          if res.skills[task2.skills_required[0]] >= task2.skills_required[1]]

                    if len(capable_resources1) > len(capable_resources2):
                        task_to_reassign = task_id1
                        other_task = task_id2
                        other_task_hour = hour2
                        current_task_hour = hour1
                    elif len(capable_resources1) < len(capable_resources2):
                        task_to_reassign = task_id2
                        other_task = task_id1
                        other_task_hour = hour1
                        current_task_hour = hour2
                    else:
                        task_to_reassign = random.choice([task_id1, task_id2])
                        if task_to_reassign == task_id1:
                            other_task = task_id2
                            other_task_hour = hour2
                            current_task_hour = hour1
                        else:
                            other_task = task_id1
                            other_task_hour = hour1
                            current_task_hour = hour2

                    new_resource = min(capable_resources1 if task_to_reassign == task_id1 else capable_resources2,
                                       key=lambda res_id: (len(resource_task_mapping.get(res_id, [])),
                                                           resource_availability[res_id]))

                    # Reassign the task to the new resource
                    available_time = max(resource_availability[new_resource],
                                         other_task_hour + instance.tasks[other_task].duration)

                    for res, task in solution.schedule[current_task_hour]:
                        if task == task_to_reassign:
                            solution.schedule[current_task_hour].remove((res, task))
                            solution.schedule[current_task_hour].append((new_resource, task))
                            break

                    # Update resource availability
                    task_end_time = available_time + instance.tasks[task_to_reassign].duration
                    resource_availability[new_resource] = task_end_time

        # Add remaining tasks to the ordered list
        for hour, assignments in solution.schedule.items():
            for resource, task_id in assignments:
                if (resource, task_id) not in ordered_list:
                    ordered_list.append((resource, task_id))

        # Update the schedule using the ordered list
        solution.schedule = self.update_schedule(ordered_list)
        solution.is_changed = True

    # end of mutation ==================================================================================================================================

    # SWAP mutation ==================================================================================================================================
    def mutationSwap(self, solution):
        instance = self.algorithm.instance

        random_task = instance.tasks[random.choice(list(instance.tasks.keys()))]

        capable_resources = [res_id for res_id, res in instance.resources.items()
                             if res.skills[random_task.skills_required[0]] >= random_task.skills_required[1]]

        flatten_list = [(resource, task) for hour, assignments in solution.schedule.items() for resource, task in
                        assignments]

        current_resource = [resource for resource, task in flatten_list if task == random_task.task_id][0]

        if len(capable_resources) > 1:
            new_resource = random.choice(list(filter(lambda x: x != current_resource, capable_resources)))
            flatten_list = [(new_resource, task) if task == random_task.task_id else (resource, task) for
                            resource, task in flatten_list]

        solution.schedule = self.update_schedule(flatten_list)

    # end of mutationSWAP ==================================================================================================================================

    # SWAP mutation ==================================================================================================================================
    def mutationTheCheapest(self, solution):
        instance = self.algorithm.instance

        random_task = instance.tasks[random.choice(list(instance.tasks.keys()))]

        capable_resources = [res_id for res_id, res in instance.resources.items()
                             if res.skills[random_task.skills_required[0]] >= random_task.skills_required[1]]

        flatten_list = [(resource, task) for hour, assignments in solution.schedule.items() for resource, task in
                        assignments]

        current_resource = [resource for resource, task in flatten_list if task == random_task.task_id][0]
        capable_resources = list(filter(lambda x: x != current_resource, capable_resources))

        capable_resources_with_salary = [(res, instance.resources[res].salary) for res in capable_resources]

        if len(capable_resources) > 1:
            new_resource1 = sorted(capable_resources_with_salary, key=lambda x: x[1])[0][0]
            new_resource2 = sorted(capable_resources_with_salary, key=lambda x: x[1])[1][0]

            count_res1 = len([resource for resource, task in flatten_list if resource == new_resource1])
            count_res2 = len([resource for resource, task in flatten_list if resource == new_resource2])

            if count_res1 < count_res2:
                new_resource = new_resource1
            else:
                new_resource = new_resource2

            flatten_list = [(new_resource, task) if task == random_task.task_id else (resource, task) for
                            resource, task in flatten_list]

        solution.schedule = self.update_schedule(flatten_list)

    # end of mutationSWAP ==================================================================================================================================

    # DHGA crossover proposed by Mehdi Deiranlou and Fariborz Jolai in 2009 =================================================================
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

    # end of crossover ==================================================================================================================================

    def PMXCrossover(self, parent1, parent2):
        child = Solution()
        instance = self.algorithm.instance
        flatten_parent1 = [(resource, task) for hour, assignments in parent1.schedule.items() for resource, task in
                           assignments]
        flatten_parent2 = [(resource, task) for hour, assignments in parent2.schedule.items() for resource, task in
                           assignments]

        # Select two random points for crossover
        crossover_points = random.sample(instance.tasks.keys(), 2)
        crossover_points.sort()

        flatten_child = [(None, task) for (_, task) in flatten_parent1]

        # middle part filled
        flatten_child = [
            (parent_tuple[0], child_tuple[1]) if crossover_points[0] <= child_tuple[1] <= crossover_points[1]
            else child_tuple
            for parent_tuple, child_tuple in zip(flatten_parent1, flatten_child)]

        # first and last part filled with parent2

        parent2_dict = {task: resource for resource, task in flatten_parent2}

        flatten_child = [(parent2_dict[task], task) if crossover_points[0] > task or task > crossover_points[1]
                         else (resource, task)
                         for resource, task in flatten_child]

        child.schedule = self.update_schedule(flatten_child)
        child.is_changed = True

        return child

    def update_schedule(self, ordered_list):
        """
        As a parameter it takes list of tuples (resource, task) in order of the schedule. And it builds the schedule/
        :param ordered_list: list of tuples (resource, task) in order of the schedule
        :return: dictionary of schedule
        """

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
