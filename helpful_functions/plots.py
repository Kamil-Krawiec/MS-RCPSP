import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("../problem_files/solutions/data.csv")

grouped_data = df.groupby(['num_ants', 'version'])

average_cost = grouped_data['cost'].mean()
average_duration = grouped_data['duration'].mean()

unstacked_cost = average_cost.unstack()
unstacked_duration = average_duration.unstack()

fig, (ax1, ax2) = plt.subplots(1, 2)

unstacked_cost.plot(kind='bar', colormap='Set3', ax=ax1)
ax1.set_xlabel('Number of ants')
ax1.set_ylabel('Average Cost')
ax1.set_title('Average Cost by Number of ants and Version')
ax1.legend(title='Version')

unstacked_duration.plot(kind='bar', colormap='Set3', ax=ax2)
ax2.set_xlabel('Number of ants')
ax2.set_ylabel('Average Duration')
ax2.set_title('Average Duration by Number of ants and Version')
ax2.legend(title='Version')

plt.tight_layout()
plt.show()
