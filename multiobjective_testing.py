import copy

from algorithms import MultiobjectiveAlgorithm
from classes.Instance import Instance
from classes.InstanceReader import InstanceReader
from classes.Solution import Solution
from optimizers import MultiobjectiveOptimizer
from Helpfull_functions import *

instances = ['100_5_20_9_D3.def', '100_10_27_9_D2.def', '100_10_48_15.def', '100_20_23_9_D1.def', '100_20_65_15.def', '200_10_85_15.def', '200_40_130_9_D4.def', '200_40_90_9.def', ]

for instance_name in instances:

    # instance_name = '200_40_90_9.def'

    reader = InstanceReader()
    try:
        resources, tasks, number_of_relations, number_of_skills = reader.read(
            f'./problem_files/instances/{instance_name}')
        instance = Instance(tasks, resources, number_of_relations, number_of_skills)
    except ValueError:
        print(f'Error in instance {instance_name}')
        continue

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

    bks10, bks13 = read_best_known_solutions(multiobjective_algorithm, instance_name)

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

            # if first_iteration:
            #     plot(multiobjective_optimizer, True, best_known_solution_10=bks10, best_known_solution_13=bks13)
            #     first_iteration = False

            multiobjective_optimizer.optimize()

            plot(multiobjective_optimizer, False, best_known_solution_10=bks10, best_known_solution_13=bks13)
            optimizers.append(copy.deepcopy(multiobjective_optimizer))

            multiobjective_algorithm.clear_population()

    plot_all_pareto_fronts(optimizers, best_known_solution_10=bks10, best_known_solution_13=bks13)
