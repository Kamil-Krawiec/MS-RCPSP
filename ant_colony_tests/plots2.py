import matplotlib.pyplot as plt
from .algorithms.MultiobjectiveAlgorithm import MultiobjectiveAlgorithm
from .classes.Solution import Solution
from .classes.InstanceReader import InstanceReader
from .classes.Instance import Instance
import pandas as pd 

instance_name = "200_20_150_9_D5.def"
instance_reader = InstanceReader()
resources, tasks, number_of_relations, number_of_skills = instance_reader.read(f"problem_files/instances/{instance_name}")
instance = Instance(tasks, resources, number_of_relations, number_of_skills)
moa = MultiobjectiveAlgorithm(instance)

best1 = Solution()
best2 = Solution()
best1.read_from_file(f"problem_files/best_found_solutions_duration_10/{instance_name}.sol")
best2.read_from_file(f"problem_files/best_found_solutions_duration_13/{instance_name}.sol")
moa.execute_solution(best1)
moa.execute_solution(best2)


df = pd.read_csv("../problem_files/solutions/data.csv")

filtered_df = df[df['instance'] == instance_name]

costs1 = []
durations1 = []
costs2 = []
durations2 = []

for index, row in filtered_df.iterrows():
  if row["version"] == 1:
    costs1.append(row["cost"])
    durations1.append(row["duration"])
  elif row["version"] == 2:
    costs2.append(row["cost"])
    durations2.append(row["duration"])

plt.scatter(durations1, costs1, label="version1", alpha=0.6)
plt.scatter(durations2, costs2, label="version2", alpha=0.6)

plt.xlabel("Duration")
plt.ylabel("Cost")
plt.scatter(best1.duration, best1.cost, label='best1', alpha=0.6)
plt.scatter(best2.duration, best2.cost, label='best2', alpha=0.6)
plt.legend()
plt.title(instance_name)
plt.show()
