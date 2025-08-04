"""
Bellman-Ford Algorithm Implementation for Flight Route Optimization

The graph data is available in: ../../output/graph_bellman_ford.json
Format: {"nodes": [...], "edges": [[source, dest, weight], ...]}
"""

import json
import time
from typing import Dict, List, Tuple, Optional

def bellman_ford(nodes: List[str], edges: List[List], start: str) -> Tuple[Dict[str, float], Dict[str, Optional[str]]]:
    """
    Bellman-Ford algorithm implementation.
    
    Args:
        nodes: List of node names (cities)
        edges: List of edges as [source, destination, weight]
        start: Starting node
        
    Returns:
        Tuple of (distances dict, predecessors dict)
    """
    # Initialize distances and predecessors
    distances = {node: float('inf') for node in nodes}
    distances[start] = 0
    predecessors = {node: None for node in nodes}
    
    # Relax edges |V| - 1 times
    n = len(nodes)
    for i in range(n - 1):
        updated = False
        for source, dest, weight in edges:
            if distances[source] != float('inf') and distances[source] + weight < distances[dest]:
                distances[dest] = distances[source] + weight
                predecessors[dest] = source
                updated = True
        
        # Early termination if no updates
        if not updated:
            break
    
    # Check for negative cycles
    for source, dest, weight in edges:
        if distances[source] != float('inf') and distances[source] + weight < distances[dest]:
            raise ValueError("Negative cycle detected in the graph!")
    
    return distances, predecessors


def find_shortest_path(graph_file: str, start: str, end: str) -> Dict:
    """
    Find shortest path between two cities using Bellman-Ford algorithm.
    
    Args:
        graph_file: Path to the graph JSON file
        start: Starting city code
        end: Destination city code
        
    Returns:
        Dictionary containing path details and metrics
    """
    start_time = time.time()
    
    # Load graph data
    with open(graph_file, 'r') as f:
        graph_data = json.load(f)
    
    nodes = graph_data['nodes']
    edges = graph_data['edges']
    
    # Validate input cities
    if start not in nodes:
        return {
            'path': None,
            'cost': float('inf'),
            'error': f"Starting city '{start}' not found in graph",
            'execution_time': time.time() - start_time
        }
    
    if end not in nodes:
        return {
            'path': None,
            'cost': float('inf'),
            'error': f"Destination city '{end}' not found in graph",
            'execution_time': time.time() - start_time
        }
    
    try:
        # Run Bellman-Ford algorithm
        distances, predecessors = bellman_ford(nodes, edges, start)
        
        # Check if destination is reachable
        if distances[end] == float('inf'):
            return {
                'path': None,
                'cost': float('inf'),
                'error': f"No route found from {start} to {end}",
                'execution_time': time.time() - start_time
            }
        
        # Reconstruct path
        path = []
        current = end
        while current is not None:
            path.append(current)
            current = predecessors[current]
        path.reverse()
        
        # Calculate execution time
        execution_time = time.time() - start_time
        
        return {
            'path': path,
            'cost': distances[end],
            'stops': len(path) - 1,
            'execution_time': execution_time,
            'algorithm': 'Bellman-Ford'
        }
        
    except ValueError as e:
        return {
            'path': None,
            'cost': float('-inf'),
            'error': str(e),
            'execution_time': time.time() - start_time
        }


def analyze_all_routes_from_city(graph_file: str, start: str) -> Dict:
    """
    Find shortest paths from a city to all other cities.
    
    Args:
        graph_file: Path to the graph JSON file
        start: Starting city code
        
    Returns:
        Dictionary with routes to all reachable cities
    """
    start_time = time.time()
    
    # Load graph data
    with open(graph_file, 'r') as f:
        graph_data = json.load(f)
    
    nodes = graph_data['nodes']
    edges = graph_data['edges']
    
    if start not in nodes:
        return {
            'error': f"Starting city '{start}' not found in graph",
            'execution_time': time.time() - start_time
        }
    
    try:
        # Run Bellman-Ford algorithm
        distances, predecessors = bellman_ford(nodes, edges, start)
        
        # Build results for all destinations
        routes = {}
        for dest in nodes:
            if dest == start:
                continue
                
            if distances[dest] == float('inf'):
                routes[dest] = {
                    'reachable': False,
                    'cost': float('inf')
                }
            else:
                # Reconstruct path
                path = []
                current = dest
                while current is not None:
                    path.append(current)
                    current = predecessors[current]
                path.reverse()
                
                routes[dest] = {
                    'reachable': True,
                    'path': path,
                    'cost': distances[dest],
                    'stops': len(path) - 1
                }
        
        return {
            'source': start,
            'routes': routes,
            'total_reachable': sum(1 for r in routes.values() if r['reachable']),
            'execution_time': time.time() - start_time
        }
        
    except ValueError as e:
        return {
            'error': str(e),
            'execution_time': time.time() - start_time
        }


def compare_routes(graph_file: str, routes_to_test: List[Tuple[str, str]]) -> List[Dict]:
    """
    Compare multiple routes for benchmarking.
    
    Args:
        graph_file: Path to the graph JSON file
        routes_to_test: List of (source, destination) tuples
        
    Returns:
        List of route results for comparison
    """
    results = []
    
    for source, dest in routes_to_test:
        result = find_shortest_path(graph_file, source, dest)
        result['route'] = f"{source} → {dest}"
        results.append(result)
    
    return results


if __name__ == "__main__":
    # Path to the graph file
    graph_file = "output/graph_bellman_ford.json"
    
    print("=== Bellman-Ford Algorithm for Flight Route Optimization ===\n")
    
    # Find route from Bangalore to Delhi
    print("Test 1: BLR (Bangalore) to DEL (Delhi)")
    result = find_shortest_path(graph_file, "BLR", "DEL")
    if result.get('error'):
        print(f"Error: {result['error']}")
    else:
        print(f"Path: {' → '.join(result['path'])}")
        print(f"Total Cost: ₹{result['cost']:,.2f}")
        print(f"Number of Stops: {result['stops']}")
        print(f"Execution Time: {result['execution_time']:.4f} seconds")
    
    print("\n" + "="*50 + "\n")
    
    # Find route requiring connections
    print("Test 2: MAA (Chennai) to AMD (Ahmedabad)")
    result = find_shortest_path(graph_file, "MAA", "AMD")
    if result.get('error'):
        print(f"Error: {result['error']}")
    else:
        print(f"Path: {' → '.join(result['path'])}")
        print(f"Total Cost: ₹{result['cost']:,.2f}")
        print(f"Number of Stops: {result['stops']}")
        print(f"Execution Time: {result['execution_time']:.4f} seconds")
    
    print("\n" + "="*50 + "\n")
    
    # Analyze all routes from a city
    print("Test 3: All routes from CCU (Kolkata)")
    analysis = analyze_all_routes_from_city(graph_file, "CCU")
    if analysis.get('error'):
        print(f"Error: {analysis['error']}")
    else:
        print(f"Total reachable cities: {analysis['total_reachable']}")
        print(f"Execution Time: {analysis['execution_time']:.4f} seconds")
        print("\nTop 5 cheapest destinations:")
        
        # Sort by cost and show top 5
        sorted_routes = sorted(
            [(dest, info) for dest, info in analysis['routes'].items() if info['reachable']],
            key=lambda x: x[1]['cost']
        )[:5]
        
        for dest, info in sorted_routes:
            print(f"  {dest}: ₹{info['cost']:,.2f} ({info['stops']} stop{'s' if info['stops'] != 1 else ''})")
    
    print("\n" + "="*50 + "\n")
    
    # Compare multiple routes
    print("Test 4: Route Comparison")
    test_routes = [
        ("BLR", "DEL"),
        ("CCU", "BOM"),
        ("DEL", "MAA"),
        ("BOM", "HYD")
    ]
    
    comparisons = compare_routes(graph_file, test_routes)
    print(f"{'Route':<15} {'Cost':<12} {'Stops':<8} {'Time (s)':<10}")
    print("-" * 50)
    for comp in comparisons:
        if comp.get('error'):
            print(f"{comp['route']:<15} {'Error':<12} {'-':<8} {comp['execution_time']:<10.4f}")
        else:
            print(f"{comp['route']:<15} ₹{comp['cost']:<11,.2f} {comp['stops']:<8} {comp['execution_time']:<10.4f}")
