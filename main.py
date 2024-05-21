from InstanceReader import InstanceReader
from Instance import Instance
from algorithms.RandomAlgorithm import RandomAlgorithm
from optimizers.SimpleOptimizer import SimpleOptimizer

reader = InstanceReader()
resources, tasks, number_of_relations, number_of_skills = reader.read('instances/15_9_12_9.def')

instance = Instance(tasks, resources, number_of_relations, number_of_skills)
instance.print_tasks()
instance.print_resources()

random_algorithm = RandomAlgorithm(instance)
optimizer = SimpleOptimizer(random_algorithm)

optimizer.initialize()
optimizer.optimize()
sol = optimizer.algorithm.population[0]
print(sol)
print(optimizer.algorithm.validate_solution(sol))



