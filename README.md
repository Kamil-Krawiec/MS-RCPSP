# MS-RCPSP Optimization using Ant Colony and NSGA-II

**Authors: Kamil Krawiec (260330), Maciej Sieroń (261704)**

**Date: June 24, 2024**

## Based on research

http://imopse.ii.pwr.wroc.pl/psp_problem.html

## Documentation

Full documentation is available [here](https://kamil-krawiec.github.io/MS-RCPSP/documentation.pdf).

### Overview

This project presents a solution to the Multi-Skill Resource-Constrained Project Scheduling Problem (MS-RCPSP) using two
advanced algorithms:

1. Ant Colony Optimization (ACO)
2. Non-dominated Sorting Genetic Algorithm II (NSGA-II)

The MS-RCPSP extends the classical RCPSP by incorporating diverse skill sets required for tasks, adding complexity to
the scheduling and optimization problem.

### Project Features

1. **Ant Colony Optimization**: Mimics the pheromone-based pathfinding behavior of ants to find efficient task
   scheduling.
2. **NSGA-II**: Addresses multi-objective optimization, balancing cost and duration in project schedules.

### Key Findings

1. **Ant Colony Optimization**: The version optimized for duration achieved better results with a larger number of ants,
   while cost-optimized version performed better with smaller number of ants.
2. **NSGA-II**: Successfully balanced multiple objectives, showing significant improvements in both cost and duration
   across various instances.

## Conclusion

Our approach to MS-RCPSP through hybrid ACO and NSGA-II demonstrates a significant potential for solving complex
scheduling problems efficiently. The algorithms provide a balanced solution that optimizes both project duration and
cost, addressing the multi-skill requirement of modern project management.