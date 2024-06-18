import csv
import json

with open('results.json', 'r') as file:
    data = json.load(file)

keys = ['instance', 'num_ants', 'alpha', 'beta', 'version']  # Get keys from the first element
keys.extend(["cost", "duration"])  # Add "cost" and "duration"

# Open the CSV file for writing (with newline='') to avoid potential issues
with open("data.csv", "w", newline="") as csvfile:
  writer = csv.writer(csvfile)
  writer.writerow(keys)  # Write header row

  # Iterate through data and write rows
  for key, value in data.items():
    row = key.split(",") + value
    writer.writerow(row)