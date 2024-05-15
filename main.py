from instance_reader import InstanceReader
from Classes import *

reader = InstanceReader('instances/100_5_20_9_D3.def')
reader.read()

instance = Instance(reader.make_instances_tasks(), reader.make_instances_resources())
instance.print_tasks()
instance.print_resources()
