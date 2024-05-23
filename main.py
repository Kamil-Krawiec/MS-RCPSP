from InstanceReader import InstanceReader
from Instance import Instance
from algorithms.RandomAlgorithm import RandomAlgorithm
from optimizers.SimpleOptimizer import SimpleOptimizer
from AntColony import AntColonyOptimizer
from Validator import validate_solution

instance_name = '200_40_90_9.def'

reader = InstanceReader()
resources, tasks, number_of_relations, number_of_skills = reader.read(f'instances/{instance_name}')

instance = Instance(tasks, resources, number_of_relations, number_of_skills)

random_algorithm = RandomAlgorithm(instance)
optimizer = SimpleOptimizer(random_algorithm)

optimizer.initialize()
optimizer.optimize()
print("worst random "+str(optimizer.get_statistics()[0].fitness))
print("best random "+str(optimizer.get_statistics()[1].fitness))

aco = AntColonyOptimizer(instance, 50, 10, 1.0, 1.0, 0.2)
aco_solution = aco.run()
print(aco.fitness(aco_solution))
print(validate_solution(aco_solution, instance))

