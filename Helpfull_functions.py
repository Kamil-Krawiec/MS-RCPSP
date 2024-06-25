import matplotlib.pyplot as plt
import os
import copy
from classes.Solution import Solution
import pandas as pd


def extract_uppercase(s):
    return ''.join([char for char in s if char.isupper()])


def generate_unique_filename(base_dir, base_name, extension="png"):
    if base_name.endswith(f".{extension}"):
        base_name = base_name[:-len(f".{extension}")]

    counter = 1
    filename = f"{base_name}.{extension}"
    while os.path.exists(os.path.join(base_dir, filename)):
        filename = f"{base_name}_{counter}.{extension}"
        counter += 1
    return os.path.join(base_dir, filename)


def plot(multiobjective_optimizer_arg, first_population=False, best_known_solution_10=None,
         best_known_solution_13=None):
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
    if best_known_solution_10:
        plt.scatter([best_known_solution_10.duration], [best_known_solution_10.cost], color='green', s=100,
                    label='BKS 10', marker='*')

    if best_known_solution_13:
        plt.scatter([best_known_solution_13.duration], [best_known_solution_13.cost], color='green', s=100,
                    label='BKS 13', marker='o')

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
    plt.savefig(generate_unique_filename('plots', title, 'png'))
    plt.show()


def plot_all_pareto_fronts(optimizers_arg, best_known_solution_10=None, best_known_solution_13=None):
    plt.figure(figsize=(12, 10))

    colors = ['red', 'blue', 'green', 'purple', 'orange', 'olive', 'brown', 'pink', 'grey']
    labels = []

    for idx, optimizer in enumerate(optimizers_arg):
        # Get Pareto front solutions
        pareto_front = optimizer.pareto_front()

        # Sort solutions by duration
        pareto_front_sorted = sorted(pareto_front, key=lambda x: x.duration)
        pareto_durations = [solution.duration for solution in pareto_front_sorted]
        pareto_costs = [solution.cost for solution in pareto_front_sorted]

        color = colors[idx % len(colors)]
        name = optimizer.name.split('_')[0] + "_" + optimizer.name.split('_')[1]
        label = f'{name} PF'
        labels.append(label)

        # Plot Pareto front solutions
        plt.scatter(pareto_durations, pareto_costs, color=color, label=label, alpha=0.8)

        # Connect Pareto front solutions
        plt.plot(pareto_durations, pareto_costs, color=color, alpha=0.6)

    # Plot best-known solution if provided
    if best_known_solution_10:
        plt.scatter([best_known_solution_10.duration], [best_known_solution_10.cost], color='black', s=100,
                    label='BKS 10', marker='*')

    if best_known_solution_13:
        plt.scatter([best_known_solution_13.duration], [best_known_solution_13.cost], color='black', s=100,
                    label='BKS 13', marker='o')

    multiobjective_optimizer_arg = optimizers_arg[0]

    instance_name = '_'.join(multiobjective_optimizer_arg.name.split('_')[2:])
    ant_colony_duration = parse_data('problem_files/solutions/duration.csv', instance_name + '.def')
    ant_colony_cost = parse_data('problem_files/solutions/cost.csv', instance_name + '.def')

    if ant_colony_duration and ant_colony_cost:
        plt.scatter([ant_colony_duration.duration], [ant_colony_duration.cost], color='black', s=100,
                    label='Ant colony duration', marker='s')
        plt.scatter([ant_colony_cost.duration], [ant_colony_cost.cost], color='black', s=100,
                    label='Ant colony cost', marker='s')

    # Title and labels
    plt.title(f"Overlay of Pareto Fronts instance {instance_name}")
    plt.xlabel('Duration')
    plt.ylabel('Cost')
    plt.yscale('log')
    plt.legend(loc='lower right')
    plt.grid(True)

    textstr = (f'Population Size: {multiobjective_optimizer_arg.POPULATION_SIZE}\n'
               f'Num Generations: {multiobjective_optimizer_arg.NUM_GENERATIONS}\n'
               f'Crossover Probability: {multiobjective_optimizer_arg.CROSSOVER_PROBABILITY}\n'
               f'Mutation Probability: {multiobjective_optimizer_arg.MUTATION_PROBABILITY}\n'
               f'Tournament Size: {multiobjective_optimizer_arg.TOURNAMENT_SIZE}\n'
               f'Other Mutation Probability: {multiobjective_optimizer_arg.OTHER_MUTATION_PROBABILITY}\n\n')

    # Adjust the figure to make room for the text box below the chart
    plt.subplots_adjust(bottom=0.25)  # Increase bottom margin to make more space

    # Add a text box below the chart
    plt.figtext(0.5, 0.01, textstr, ha='center', fontsize=10,
                bbox=dict(facecolor='white', alpha=0.8))

    # Generate unique filename
    base_dir = 'plots'
    base_name = 'all_pareto_fronts_line'
    filename = generate_unique_filename(base_dir, base_name)

    plt.savefig(filename, bbox_inches='tight')  # Ensure everything fits within the saved plot
    plt.show()


def read_best_known_solutions(multiobjective_algorithm, instance_name):
    if os.path.isfile('problem_files/best_found_solutions_duration_10/' + instance_name + '.sol'):
        best_known_solution_duration_10 = Solution()
        best_known_solution_duration_10.read_from_file(
            f'./problem_files/best_found_solutions_duration_10/{instance_name}.sol')
        multiobjective_algorithm.execute_solution(best_known_solution_duration_10)
    else:
        best_known_solution_duration_10 = None

    if os.path.isfile('problem_files/best_found_solutions_duration_13/' + instance_name + '.sol'):
        best_known_solution_duration_13 = Solution()
        best_known_solution_duration_13.read_from_file(
            f'./problem_files/best_found_solutions_duration_13/{instance_name}.sol')
        multiobjective_algorithm.execute_solution(best_known_solution_duration_13)
    else:
        best_known_solution_duration_13 = None

    return best_known_solution_duration_10, best_known_solution_duration_13


def parse_data(file_path, instance_name):
    # Read CSV file into DataFrame
    df = pd.read_csv(file_path)

    # Filter rows by instance name
    instance_rows = df[df['instance'] == instance_name]
    solution = Solution()
    solution.set_cost(instance_rows['cost'])
    solution.set_duration(instance_rows['duration'])
    return solution