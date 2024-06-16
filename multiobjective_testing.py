import matplotlib.pyplot as plt
import os
from classes.Solution import Solution
from classes.Instance import Instance
from classes.InstanceReader import InstanceReader
from algorithms import MultiobjectiveAlgorithm
from optimizers import MultiobjectiveOptimizer


def plot(multiobjective_optimizer_arg, first_population=False, best_known_solution=None):
    title = multiobjective_optimizer_arg.name

    # Collect duration and cost values
    durations = [solution.duration for solution in multiobjective_optimizer_arg.algorithm.population]
    costs = [solution.cost for solution in multiobjective_optimizer_arg.algorithm.population]

    # Get Pareto front solutions
    pareto_front = multiobjective_optimizer_arg.pareto_front()
    pareto_durations = [solution.duration for solution in pareto_front]
    pareto_costs = [solution.cost for solution in pareto_front]

    # Plot the data
    plt.figure(figsize=(10, 8))

    # Plot all solutions
    plt.scatter(durations, costs, color='blue', label='Non-Pareto Solutions', alpha=0.6)

    # Plot Pareto front solutions separately to mark them
    plt.scatter(pareto_durations, pareto_costs, color='red', label='Pareto Front', alpha=0.8)

    # Plot best-known solution if provided
    if best_known_solution:
        plt.scatter([best_known_solution.duration], [best_known_solution.cost], color='green', s=100,
                    label='Best Known Solution', marker='*')

    # Title with algorithm name
    plt.title(f'Duration vs Cost - {title}')
    plt.xlabel('Duration')
    plt.ylabel('Cost')
    plt.legend()
    plt.grid(True)

    # Text box with statistics
    textstr = (f'Population Size: {multiobjective_optimizer_arg.POPULATION_SIZE}\n'
               f'Num Generations: {multiobjective_optimizer_arg.NUM_GENERATIONS}\n'
               f'Crossover Probability: {multiobjective_optimizer_arg.CROSSOVER_PROBABILITY}\n'
               f'Mutation Probability: {multiobjective_optimizer_arg.MUTATION_PROBABILITY}\n'
               f'Tournament Size: {multiobjective_optimizer_arg.TOURNAMENT_SIZE}\n\n')

    plt.gca().text(0.95, 0.05, textstr, transform=plt.gca().transAxes, fontsize=10,
                   verticalalignment='bottom', horizontalalignment='right',
                   bbox=dict(facecolor='white', alpha=0.8))

    if first_population:
        plt.savefig(f'plots/{title}_first_population.png')
    plt.savefig(f'plots/{title}.png')
    plt.show()


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
    MultiobjectiveOptimizer.MultiobjectiveOptimizer.mutationSwap,
    MultiobjectiveOptimizer.MultiobjectiveOptimizer.mutationTheCheapest,
    MultiobjectiveOptimizer.MultiobjectiveOptimizer.mutationDurationOptimized]

multiobjective_algorithm = MultiobjectiveAlgorithm.MultiobjectiveAlgorithm(instance)

if os.path.isfile('problem_files/best_found_solutions_duration_10/' + instance_name + '.sol'):
    best_known_solution_duration = Solution()
    best_known_solution_duration.read_from_file(f'./problem_files/best_found_solutions_duration_10/{instance_name}.sol')
    multiobjective_algorithm.execute_solution(best_known_solution_duration)

else:
    best_known_solution_duration = None

first_iteration = True

for crossover in crossovers:
    for mutation in mutations:
        multiobjective_optimizer = MultiobjectiveOptimizer.MultiobjectiveOptimizer(multiobjective_algorithm,
                                                                                   crossover,
                                                                                   mutation,
                                                                                   f'{crossover.__name__}_{mutation.__name__}_{instance_name}')

        multiobjective_optimizer.initialize()
        multiobjective_optimizer.evaluate()

        if first_iteration:
            plot(multiobjective_optimizer, True, best_known_solution=best_known_solution_duration)
            first_iteration = False

        multiobjective_optimizer.optimize()

        plot(multiobjective_optimizer, False, best_known_solution=best_known_solution_duration)

        multiobjective_algorithm.clear_population()
