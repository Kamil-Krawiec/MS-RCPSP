from InstanceReader import InstanceReader
from Instance import Instance
from algorithms import RandomAlgorithm, MultiobjectiveAlgorithm
from optimizers import SimpleOptimizer, MultiobjectiveOptimizer
import matplotlib.pyplot as plt


def plot(multiobjective_optimizer_arg, first_population=False):
    title = multiobjective_optimizer_arg.name
    # Collect duration and cost values
    durations = [solution.duration for solution in multiobjective_optimizer_arg.algorithm.population]
    costs = [solution.cost for solution in multiobjective_optimizer_arg.algorithm.population]

    # Get Pareto front solutions
    pareto_front = multiobjective_optimizer_arg.pareto_front()
    pareto_durations = [solution.duration for solution in pareto_front]
    pareto_costs = [solution.cost for solution in pareto_front]

    # Calculate statistics
    avg_duration = sum(durations) / len(durations)
    avg_cost = sum(costs) / len(costs)
    avg_pareto_duration = sum(pareto_durations) / len(pareto_durations)
    avg_pareto_cost = sum(pareto_costs) / len(pareto_costs)

    # Plot the data
    plt.figure(figsize=(10, 8))

    # Plot all solutions
    plt.scatter(durations, costs, color='blue', label='Non-Pareto Solutions', alpha=0.6)

    # Plot Pareto front solutions separately to mark them
    plt.scatter(pareto_durations, pareto_costs, color='red', label='Pareto Front', alpha=0.8)

    # Title with algorithm name
    plt.title(f'Duration vs Cost - {title}')
    plt.xlabel('Duration')
    plt.ylabel('Cost')
    plt.legend()
    plt.grid(True)

    # Text box with statistics
    textstr = (f'Total Solutions: {len(durations)}\n'
               f'Pareto Solutions: {len(pareto_durations)}\n\n'
               f'Avg Duration (All): {avg_duration:.2f}\n'
               f'Avg Cost (All): {avg_cost:.2f}\n\n'
               f'Avg Duration (Pareto): {avg_pareto_duration:.2f}\n'
               f'Avg Cost (Pareto): {avg_pareto_cost:.2f}')

    plt.gca().text(0.95, 0.05, textstr, transform=plt.gca().transAxes, fontsize=10,
                   verticalalignment='bottom', horizontalalignment='right',
                   bbox=dict(facecolor='white', alpha=0.8))

    if first_population:
        plt.savefig(f'plots/{title}_first_population.png')
    plt.savefig(f'plots/{title}.png')
    plt.show()


instance_name = '200_10_135_9_D6.def'

reader = InstanceReader()
resources, tasks, number_of_relations, number_of_skills = reader.read(f'instances/{instance_name}')

instance = Instance(tasks, resources, number_of_relations, number_of_skills)

crossovers = [MultiobjectiveOptimizer.MultiobjectiveOptimizer.DHGAcrossover,
              MultiobjectiveOptimizer.MultiobjectiveOptimizer.PMXCrossover]
mutations = [MultiobjectiveOptimizer.MultiobjectiveOptimizer.mutationCAM,
             MultiobjectiveOptimizer.MultiobjectiveOptimizer.mutationSwap,
             MultiobjectiveOptimizer.MultiobjectiveOptimizer.mutationTheCheapest]

for crossover in crossovers:
    for mutation in mutations:
        multiobjective_algorithm = MultiobjectiveAlgorithm.MultiobjectiveAlgorithm(instance)
        multiobjective_optimizer = MultiobjectiveOptimizer.MultiobjectiveOptimizer(multiobjective_algorithm,
                                                                                   crossover,
                                                                                   mutation,
                                                                                   f'{crossover.__name__}_{mutation.__name__}_{instance_name}')

        multiobjective_optimizer.initialize()
        multiobjective_optimizer.evaluate()

        plot(multiobjective_optimizer, True)

        multiobjective_optimizer.optimize()

        plot(multiobjective_optimizer)

        sol = multiobjective_optimizer.algorithm.population[0]
        sol.save_to_file(instance_name)
