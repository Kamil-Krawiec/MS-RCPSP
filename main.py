from InstanceReader import InstanceReader
from Instance import Instance
from algorithms.RandomAlgorithm import RandomAlgorithm
from optimizers.SimpleOptimizer import SimpleOptimizer

instance_name = '200_40_90_9.def'

reader = InstanceReader()
resources, tasks, number_of_relations, number_of_skills = reader.read(f'instances/{instance_name}')

instance = Instance(tasks, resources, number_of_relations, number_of_skills)

random_algorithm = RandomAlgorithm(instance)
optimizer = SimpleOptimizer(random_algorithm)

optimizer.initialize()
optimizer.optimize()
print("worst "+str(optimizer.get_statistics()[0].fitness))
print("best "+str(optimizer.get_statistics()[1].fitness))




