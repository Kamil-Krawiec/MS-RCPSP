from InstanceReader import InstanceReader
from Instance import Instance
from algorithms import RandomAlgorithm, MultiobjectiveAlgorithm
from optimizers import SimpleOptimizer, MultiobjectiveOptimizer
import matplotlib.pyplot as plt


def plot():
    # Plotting
    # Collect duration and cost values
    durations = [solution.duration for solution in multiobjective_optimizer.algorithm.population]
    costs = [solution.cost for solution in multiobjective_optimizer.algorithm.population]

    # Get Pareto front solutions
    pareto_front = multiobjective_optimizer.pareto_front()
    pareto_durations = [solution.duration for solution in pareto_front]
    pareto_costs = [solution.cost for solution in pareto_front]

    # Plot the data
    plt.figure(figsize=(8, 6))

    # Plot all solutions
    plt.scatter(durations, costs, color='blue', label='Non-Pareto Solutions')

    # Plot Pareto front solutions separately to mark them
    plt.scatter(pareto_durations, pareto_costs, color='red', label='Pareto Front')

    plt.title('Duration vs Cost')
    plt.xlabel('Duration')
    plt.ylabel('Cost')
    plt.legend()
    plt.grid(True)
    plt.show()


instance_name = '200_40_90_9.def'

reader = InstanceReader()
resources, tasks, number_of_relations, number_of_skills = reader.read(f'instances/{instance_name}')

instance = Instance(tasks, resources, number_of_relations, number_of_skills)

random_algorithm = RandomAlgorithm.RandomAlgorithm(instance)
optimizer = SimpleOptimizer.SimpleOptimizer(random_algorithm)

optimizer.initialize()
optimizer.optimize()
print("worst " + str(optimizer.get_statistics()[0].fitness))
print("best " + str(optimizer.get_statistics()[1].fitness))

multiobjective_algorithm = MultiobjectiveAlgorithm.MultiobjectiveAlgorithm(instance)
multiobjective_optimizer = MultiobjectiveOptimizer.MultiobjectiveOptimizer(multiobjective_algorithm)

multiobjective_optimizer.initialize()
multiobjective_optimizer.optimize()
multiobjective_optimizer.non_dominated_sort()
print()



