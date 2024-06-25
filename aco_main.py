from classes.InstanceReader import InstanceReader
from classes.Instance import Instance
from algorithms.AntColony import AntColonyOptimizer
from classes.Validator import validate_solution
import json
import os 

instances = []
reader = InstanceReader()
for file in os.listdir("problem_files/instances"):
    try:
        resources, tasks, number_of_relations, number_of_skills = reader.read(f"problem_files/instances/{file}")
        instance = Instance(tasks, resources, number_of_relations, number_of_skills, file)
        instances.append(instance)
    except Exception as e:
        print(e)

# random_algorithm = RandomAlgorithm(instance)
# optimizer = SimpleOptimizer(random_algorithm)

# optimizer.initialize()
# optimizer.optimize()
# print("worst random "+str(optimizer.get_statistics()[0].fitness))
# print("best random "+str(optimizer.get_statistics()[1].fitness))

# aco_optimizer = AntColonyOptimizer(instance, 50, 5, 1.0, 1.0, 0.5)
# aco_solution1 = aco_optimizer.run(1)
# aco_solution2 = aco_optimizer.run(2)
# aco_solution1.save_to_file("solution1")
# aco_solution2.save_to_file("solution2")

results = {}

for instance in instances:
    for num_ants in [1, 30]:
        for alpha, beta in [(1.0, 5.0), (5.0, 1.0), (1.0, 1.0)]:
            for evaporation in [0.1, 0.5, 0.9]:
                aco_optimizer = AntColonyOptimizer(instance, num_ants, 10, alpha, beta, evaporation)
                aco_solution1 = aco_optimizer.run(1)
                aco_solution2 = aco_optimizer.run(2)
                if not any([
                    validate_solution(aco_solution1, instance),
                    validate_solution(aco_solution2, instance)
                ]):
                    print("Eror: Solution not valid!")
                results[f"{instance.filepath},{num_ants},{alpha},{beta},{evaporation},1"] = (
                    int(aco_optimizer.cost(aco_solution1)),
                    aco_optimizer.duration(aco_solution1)
                )
                results[f"{instance.filepath},{num_ants},{alpha},{beta},{evaporation},2"] = (
                    int(aco_optimizer.cost(aco_solution2)),
                    aco_optimizer.duration(aco_solution2)
                )

with open('results.json', 'w') as f:
    f.write(json.dumps(results, indent=4))