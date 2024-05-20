from InstanceReader import InstanceReader
from Instance import Instance

reader = InstanceReader()
resources, tasks, number_of_relations, number_of_skills = reader.read('instances/100_5_20_9_D3.def')

instance = Instance(tasks, resources, number_of_relations, number_of_skills)
instance.print_tasks()
instance.print_resources()
