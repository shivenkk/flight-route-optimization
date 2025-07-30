# Flight Route Optimization

CS5800 Algorithms course project comparing graph-based approaches to find optimal flight routes using real airline data.

## Overview

This project implements and compares three algorithms for finding the cheapest flight routes while handling real-world constraints like loyalty discounts, time preferences, and connection limits.

## Algorithms Implemented

1. **Dijkstra's Algorithm** - Baseline shortest path finding
2. **Bellman-Ford Algorithm** - Handles negative edge weights from discounts
3. **Dynamic Programming** - Multi-constraint optimization (stops, time, airline preferences)