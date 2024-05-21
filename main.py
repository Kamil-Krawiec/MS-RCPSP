from InstanceReader import InstanceReader
from Instance import Instance
from algorithms.RandomAlgorithm import RandomAlgorithm
from optimizers.SimpleOptimizer import SimpleOptimizer

instance_name = '15_9_12_9.def'

reader = InstanceReader()
resources, tasks, number_of_relations, number_of_skills = reader.read(f'instances/{instance_name}')

instance = Instance(tasks, resources, number_of_relations, number_of_skills)

random_algorithm = RandomAlgorithm(instance)
optimizer = SimpleOptimizer(random_algorithm)

optimizer.initialize()
optimizer.optimize()
sol = optimizer.algorithm.population[0]
sol2 = optimizer.algorithm.population[1]
sol.save_to_file(instance_name)
sol2.save_to_file(instance_name+"2")
print(optimizer.algorithm.validate_solution(sol))
print(optimizer.algorithm.validate_solution(sol2))




