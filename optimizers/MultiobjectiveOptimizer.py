import random
import copy
from Solution import Solution
from abstractClasses.Optimizer import Optimizer


class MultiobjectiveOptimizer(Optimizer):

    def __init__(self, algorithm, crossover_method, mutation_method, name):
        super().__init__(algorithm)
        self.crossover = crossover_method
        self.mutation = mutation_method
        self.name = name

    def mutation(self, solution: Solution):
        self.mutation(solution)

    def crossover(self, parent1: Solution, parent2: Solution):
        return self.crossover(parent1, parent2)

    def optimize(self):
        for generation in range(Optimizer.NUM_GENERATIONS):
            self.evaluate()
            self.non_dominated_sort()

            new_population = []
            while len(new_population) < Optimizer.POPULATION_SIZE:
                parent1 = self.selection()
                parent2 = self.selection()
                if random.random() < Optimizer.CROSSOVER_PROBABILITY:
                    child1 = self.crossover(self, parent1, parent2)
                    child2 = self.crossover(self, parent2, parent1)

                else:
                    child1 = parent1
                    child2 = parent2

                if random.random() < Optimizer.MUTATION_PROBABILITY:
                    if child1.is_changed:
                        self.algorithm.execute_solution(child1)
                    if child2.is_changed:
                        self.algorithm.execute_solution(child2)

                    self.mutation(self, child1)
                    self.mutation(self, child2)
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

    # MUTATIONS ==================================================================================================================================

    # Conflict Avoidance Mutation (CAM) proposed by Pawel B. Myszkowski, Marek E. Skowronski in 2013 =================================================================
    def mutationCAM(self, solution):
        if random.random() < self.OTHER_MUTATION_PROBABILITY:
            self.mutationTheCheapest(solution)
            return

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

    def mutationSwap(self, solution):
        if random.random() < self.OTHER_MUTATION_PROBABILITY:
            self.mutationCAM(solution)
            return

        instance = self.algorithm.instance

        genes_to_swap = len(instance.tasks) // 10  # Number of genes to swap (10% of the total number of tasks

        for _ in range(genes_to_swap):
            # Randomly select a task to swap
            random_task = instance.tasks[random.choice(list(instance.tasks.keys()))]

            # Find capable resources for the selected task
            capable_resources = [res_id for res_id, res in instance.resources.items()
                                 if res.skills[random_task.skills_required[0]] >= random_task.skills_required[1]]

            if not capable_resources:
                continue  # Skip if no capable resources found

            # Flatten schedule to list of assignments
            flatten_list = [(resource, task) for hour, assignments in solution.schedule.items() for resource, task in
                            assignments]

            # Find the current resource assigned to the selected task
            current_resources = [resource for resource, task in flatten_list if task == random_task.task_id]

            if not current_resources:
                continue  # Skip if no current resources found for the task

            current_resource = random.choice(current_resources)

            # Choose a new resource different from the current one
            new_resource = random.choice(list(filter(lambda x: x != current_resource, capable_resources)))

            # Perform the swap in the flatten_list
            flatten_list = [(new_resource, task) if task == random_task.task_id else (resource, task) for
                            resource, task in flatten_list]

            # Update the solution schedule with the modified flatten_list
            solution.schedule = self.update_schedule(flatten_list)
            solution.is_changed = True

    def mutationTheCheapest(self, solution):
        if random.random() < self.OTHER_MUTATION_PROBABILITY:
            self.mutationCAM(solution)
            return

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

    def mutationDurationOptimized(self, solution):
        if random.random() < self.OTHER_MUTATION_PROBABILITY:
            self.mutationSwap(solution)
            return

        instance = self.algorithm.instance

        # Identify critical tasks (tasks on the critical path or with minimal slack)
        critical_tasks = self.identify_critical_tasks(solution)

        if not critical_tasks:
            return  # No critical tasks identified, return without making changes

        # Randomly select a critical task
        random_task = random.choice(critical_tasks)

        # Find capable resources for the task
        capable_resources = [res_id for res_id, res in instance.resources.items()
                             if res.skills[random_task.skills_required[0]] >= random_task.skills_required[1]]

        if not capable_resources:
            return  # No capable resources found, return without making changes

        # Flatten schedule to list of assignments
        flatten_list = [(resource, task) for hour, assignments in solution.schedule.items() for resource, task in
                        assignments]

        # Find the current resource assigned to the selected task
        current_resource = next((resource for resource, task in flatten_list if task == random_task.task_id), None)
        capable_resources = list(filter(lambda x: x != current_resource, capable_resources))

        if len(capable_resources) > 1:
            best_solution = None
            best_duration = float('inf')  # Initialize with a large value

            for res_id in capable_resources:
                # Create a copy of the current solution
                temp_sol = copy.deepcopy(solution)

                # Update the schedule with the new resource assignment
                flatten_list_temp = [(res_id, task) if task == random_task.task_id else (resource, task)
                                     for resource, task in flatten_list]

                temp_sol.schedule = self.update_schedule(flatten_list_temp)

                # Execute the temporary solution
                self.algorithm.execute_solution(temp_sol)

                # Compare durations
                if temp_sol.duration < best_duration:
                    best_duration = temp_sol.duration
                    best_solution = temp_sol
                elif temp_sol.duration == best_duration and temp_sol.cost < best_solution.cost:
                    best_solution = temp_sol

            if best_solution:
                # Update the original solution with the best found solution
                solution.schedule = best_solution.schedule
                solution.fitness = best_solution.fitness
                solution.duration = best_solution.duration
                solution.cost = best_solution.cost
                solution.is_changed = True

    def identify_critical_tasks(self, solution):
        instance = self.algorithm.instance
        tasks = list(instance.tasks.values())
        task_durations = {task.task_id: task.duration for task in tasks}

        # Calculate earliest start times and end times for each task
        earliest_start_times = {task.task_id: 0 for task in tasks}  # Initialize earliest start times

        # Calculate earliest start times using topological sorting
        sorted_tasks = self.topological_sort(tasks)

        for task in sorted_tasks:
            for predecessor_id in task.predecessor_ids:
                predecessor_end_time = earliest_start_times[predecessor_id]

                # Update earliest start time for current task
                earliest_start_times[task.task_id] = max(earliest_start_times[task.task_id],
                                                         predecessor_end_time + task_durations[predecessor_id])

        # Calculate latest end times and slack for each task
        latest_end_times = {task.task_id: earliest_start_times[task.task_id] + task_durations[task.task_id]
                            for task in tasks}

        # Calculate critical path length
        critical_path_length = max(latest_end_times.values())

        # Identify critical tasks (tasks with zero slack)
        critical_tasks = [task for task in tasks if latest_end_times[task.task_id] == critical_path_length]

        return critical_tasks

    def topological_sort(self, tasks):
        """ Perform topological sorting of tasks based on predecessors """
        visited = set()
        stack = []

        # Create a mapping from task_id to Task object for quick lookup
        task_map = {task.task_id: task for task in tasks}

        def dfs(task_id):
            task = task_map[task_id]
            if task.task_id not in visited:
                visited.add(task.task_id)
                for predecessor_id in task.predecessor_ids:
                    if predecessor_id in task_map:  # Ensure predecessor exists in task_map
                        dfs(predecessor_id)
                stack.append(task)

        # Perform DFS for each task that hasn't been visited
        for task in tasks:
            if task.task_id not in visited:
                dfs(task.task_id)

        return stack[::-1]  # Reverse the stack to get topological order

    # END MUTATIONS ==================================================================================================================================
    # CROSSOVERS ==================================================================================================================================

    # DHGA crossover proposed by Mehdi Deiranlou and Fariborz Jolai in 2009 =================================================================
    def DHGAcrossover(self, parent1, parent2):
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

    # END CROSSOVERS ==================================================================================================================================

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
