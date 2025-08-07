"""
Dijkstra Algorithm Implementation for Flight Route Optimization
Updated to work with processed flight data and discount system

The graph data is available in: graph_dijkstra.json
Format: {source_city: {dest_city: discounted_weight, ...}, ...}

Key Points:
- All weights are post-discount prices (IndiGo 15%, Jet Airways 20%, Credit Card ₹1000, Seasonal 25%)
- Dijkstra works well since all weights are positive after discount processing
- Serves as baseline to compare against Bellman-Ford results
- Expected routes: BLR→DEL (₹2,265), BOM→HYD (₹883.50), etc.
"""

import json
import heapq
import time
from typing import Dict, List, Tuple

def dijkstra(graph: Dict, start: str) -> Tuple[Dict[str, float], Dict[str, str]]:
    """
    Dijkstra algorithm implementation for flight route optimization.
    Uses pre-processed discount data.
    
    Args:
        graph: Adjacency list representation with discounted weights
        start: Starting city code
        
    Returns:
        Tuple of (distances dict, predecessors dict)
    """
    # Initialize distances and predecessors
    distances = {city: float('inf') for city in graph}
    distances[start] = 0
    predecessors = {city: None for city in graph}
    
    # Priority queue with (distance, city)
    pq = [(0, start)]
    visited = set()
    
    while pq:
        current_dist, current_city = heapq.heappop(pq)
        
        if current_city in visited:
            continue
        visited.add(current_city)
        
        # Check all neighbors using discounted weights
        for neighbor, discounted_weight in graph.get(current_city, {}).items():
            new_dist = current_dist + discounted_weight
            if new_dist < distances[neighbor]:
                distances[neighbor] = new_dist
                predecessors[neighbor] = current_city
                heapq.heappush(pq, (new_dist, neighbor))
    
    return distances, predecessors

def find_shortest_path(graph_file: str, start: str, end: str) -> Dict:
    """
    Find shortest path between two cities using Dijkstra on discounted weights.
    
    Args:
        graph_file: Path to graph_dijkstra.json
        start: Starting city code
        end: Destination city code
        
    Returns:
        Dictionary containing path details and metrics
    """
    start_time = time.time()
    
    # Load processed graph data
    with open(graph_file, 'r') as f:
        graph = json.load(f)
    
    # Validate input cities
    if start not in graph:
        return {
            'path': None,
            'cost': float('inf'),
            'error': f"Starting city '{start}' not found in graph",
            'execution_time': time.time() - start_time,
            'algorithm': 'Dijkstra'
        }
    
    if end not in graph:
        return {
            'path': None,
            'cost': float('inf'),
            'error': f"Destination city '{end}' not found in graph",
            'execution_time': time.time() - start_time,
            'algorithm': 'Dijkstra'
        }
    
    # Run Dijkstra algorithm on discounted weights
    distances, predecessors = dijkstra(graph, start)
    
    # Check if destination is reachable
    if distances[end] == float('inf'):
        return {
            'path': None,
            'cost': float('inf'),
            'error': f"No route found from {start} to {end}",
            'execution_time': time.time() - start_time,
            'algorithm': 'Dijkstra'
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
        'algorithm': 'Dijkstra',
        'note': 'Uses pre-discounted weights from data processing'
    }

def run_handoff_tests(graph_file: str):
    """
    Run the specific test cases mentioned in project requirements
    """
    print("=== Testing Project Requirements Examples ===\n")
    
    # Test cases from handoff
    handoff_tests = [
        ('BLR', 'DEL', 2265.0),  # Expected: direct route ₹2,265
        ('CCU', 'BOM', None),    # May benefit from multi-hop discount stacking (for Bellman-Ford)
        ('MAA', 'AMD', None),    # No direct route, requires connections
        ('BOM', 'HYD', 883.5),   # Expected: heavily discounted route ₹883.50
    ]
    
    for start, end, expected in handoff_tests:
        result = find_shortest_path(graph_file, start, end)
        
        print(f"Route: {start} → {end}")
        if result.get('error'):
            print(f"❌ Error: {result['error']}")
        else:
            print(f"✅ Path: {' → '.join(result['path'])}")
            print(f"   Cost: ₹{result['cost']:,.2f}")
            print(f"   Stops: {result['stops']}")
            print(f"   Time: {result['execution_time']:.4f}s")
            
            # Compare with expected (if provided)
            if expected:
                if abs(result['cost'] - expected) < 0.01:
                    print(f"✅ Matches expected cost (₹{expected:,.2f})")
                else:
                    print(f"⚠️  Expected ₹{expected:,.2f}, got ₹{result['cost']:,.2f}")
        print()

def analyze_discount_impact(graph_file: str):
    """
    Analyze the impact of the discount system on route pricing
    """
    print("=== Discount System Analysis ===\n")
    
    with open(graph_file, 'r') as f:
        graph = json.load(f)
    
    all_weights = []
    for city_routes in graph.values():
        all_weights.extend(city_routes.values())
    
    # Analyze price distribution
    min_weight = min(all_weights)
    max_weight = max(all_weights)
    avg_weight = sum(all_weights) / len(all_weights)
    
    print(f"📊 Price Distribution (Post-Discount):")
    print(f"   Cheapest route: ₹{min_weight:.2f}")
    print(f"   Most expensive: ₹{max_weight:.2f}")
    print(f"   Average price: ₹{avg_weight:.2f}")
    print(f"   Total routes: {len(all_weights)}")
    
    # Find heavily discounted routes (< ₹1,000 as mentioned in handoff)
    heavily_discounted = [w for w in all_weights if w < 1000]
    print(f"\n🎯 Heavily Discounted Routes (< ₹1,000): {len(heavily_discounted)}")
    
    if heavily_discounted:
        print(f"   Cheapest: ₹{min(heavily_discounted):.2f}")
        print(f"   These likely have 25% seasonal + additional discounts")
    
    # Find expensive routes (> ₹10,000 as mentioned)
    expensive_routes = [w for w in all_weights if w > 10000]
    print(f"\n💰 Expensive Routes (> ₹10,000): {len(expensive_routes)}")
    if expensive_routes:
        print(f"   Most expensive: ₹{max(expensive_routes):.2f}")
        print(f"   These likely have minimal applicable discounts")

if __name__ == "__main__":
    # Use the updated graph file
    graph_file = "graph_dijkstra.json"
    
    print("🚀 Dijkstra Algorithm - Updated with Latest Data")
    print("="*60)
    print("Key Features:")
    print("• Uses pre-discounted weights (IndiGo 15%, Jet Airways 20%, etc.)")
    print("• Baseline algorithm for team comparison")
    print("• Handles positive weights efficiently")
    print("• Won't exploit multi-hop discount opportunities (that's Bellman-Ford's job)")
    print("="*60)
    
    # Run project-specific tests
    run_handoff_tests(graph_file)
    
    # Analyze discount impact
    analyze_discount_impact(graph_file)
    
    # Additional comprehensive testing
    print("\n=== Additional Route Analysis ===")
    
    # Test hub connectivity (Delhi as major hub)
    print("\nTesting Delhi Hub Connectivity:")
    hub_routes = [('DEL', 'BOM'), ('DEL', 'BLR'), ('DEL', 'MAA'), ('DEL', 'CCU')]
    
    for start, end in hub_routes:
        result = find_shortest_path(graph_file, start, end)
        if not result.get('error'):
            print(f"  {start}→{end}: ₹{result['cost']:,.2f} ({result['stops']} stops)")
    
    # Performance summary
    print(f"\n📈 Algorithm Performance Summary:")
    print(f"   Time Complexity: O((V + E) log V)")
    print(f"   Space Complexity: O(V)")
    print(f"   Network Size: 15 cities, ~88 routes")
    print(f"   Expected Performance: Sub-millisecond execution")
    print(f"   Discount Handling: Uses pre-processed weights")
    print(f"   Team Role: Baseline for comparing Bellman-Ford & DP results")
