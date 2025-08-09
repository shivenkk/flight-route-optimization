# Flight Route Optimization

CS5800 Algorithms course project comparing graph-based approaches to find optimal flight routes using real airline data.

## Overview

This project implements and compares three algorithms for finding the cheapest flight routes while handling real-world constraints like loyalty discounts, time preferences, and connection limits.

## Algorithms Implemented

1. **Dijkstra's Algorithm** - Baseline shortest path finding
2. **Bellman-Ford Algorithm** - Handles negative edge weights from discounts
3. **Dynamic Programming** - Multi-constraint optimization (max stops, budget, airline preference)

## Data
- 10,683 Indian domestic flights
- 15 cities, 88 routes after processing
- Includes discounts (loyalty programs, seasonal offers)

## Files
- `data/` - raw flight CSV
- `src/` - algorithm implementations
- `output/` - processed graph JSONs
- `comparison_analysis.py` - performance comparison

## How to Run

Run individual algorithms:
```bash
python src/algorithms/dijkstra.py
python src/algorithms/bellman_ford.py
python src/algorithms/dynamic_programming.py
```

Compare all three:
```bash
python comparison_analysis.py
```

