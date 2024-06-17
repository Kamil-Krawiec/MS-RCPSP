import copy

from algorithms import MultiobjectiveAlgorithm
from classes.Instance import Instance
from classes.InstanceReader import InstanceReader
from classes.Solution import Solution
from optimizers import MultiobjectiveOptimizer
from Helpfull_functions import *

instance_name = '200_40_130_9_D4.def'

reader = InstanceReader()
resources, tasks, number_of_relations, number_of_skills = reader.read(f'./problem_files/instances/{instance_name}')

instance = Instance(tasks, resources, number_of_relations, number_of_skills)

crossovers = [
    MultiobjectiveOptimizer.MultiobjectiveOptimizer.DHGAcrossover,
    MultiobjectiveOptimizer.MultiobjectiveOptimizer.PMXCrossover
]

mutations = [
    MultiobjectiveOptimizer.MultiobjectiveOptimizer.mutationCAM,
    MultiobjectiveOptimizer.MultiobjectiveOptimizer.mutationSWAP,
    MultiobjectiveOptimizer.MultiobjectiveOptimizer.mutationCHEAPEST,
    MultiobjectiveOptimizer.MultiobjectiveOptimizer.mutationCPO]

multiobjective_algorithm = MultiobjectiveAlgorithm.MultiobjectiveAlgorithm(instance)

bks10,bks13 = read_best_known_solutions(multiobjective_algorithm, instance_name)


first_iteration = True
optimizers = []

for crossover in crossovers:
    for mutation in mutations:
        multiobjective_optimizer = MultiobjectiveOptimizer.MultiobjectiveOptimizer(multiobjective_algorithm,
                                                                                   crossover,
                                                                                   mutation,
                                                                                   f'{crossover.__name__[:4]}_'
                                                                                   f'{extract_uppercase(mutation.__name__)}_'
                                                                                   f'{instance_name.split(".")[0]}')

        multiobjective_optimizer.initialize()
        multiobjective_optimizer.evaluate()

        if first_iteration:
            plot(multiobjective_optimizer, True, best_known_solution_10=bks10, best_known_solution_13=bks13)
            first_iteration = False

        multiobjective_optimizer.optimize()

        # plot(multiobjective_optimizer, False, best_known_solution_10=best_known_solution_duration_10)
        optimizers.append(copy.deepcopy(multiobjective_optimizer))

        multiobjective_algorithm.clear_population()

plot_all_pareto_fronts(optimizers, best_known_solution_10=bks10,best_known_solution_13=bks13)
