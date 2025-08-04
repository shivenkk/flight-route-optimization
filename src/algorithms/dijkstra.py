"""
Dijkstra's Algorithm Implementation for Flight Route Optimization

TODO: Implement Dijkstra's algorithm for shortest path with positive weights.

The graph data is available in: ../../output/graph_dijkstra.json
Format: {source: {destination: weight, ...}, ...}
"""

import json
import heapq
import time

def dijkstra(graph, start, end):
    """Find shortest path using Dijkstra's algorithm"""
    # Set all distances to infinity except start
    distances = {city: float('inf') for city in graph}
    distances[start] = 0
    
    # Track how we got to each city
    parent = {}
    
    # Priority queue with (distance, city)
    pq = [(0, start)]
    visited = set()
    nodes_explored = 0
    
    while pq:
        dist, city = heapq.heappop(pq)
        
        if city in visited:
            continue
        visited.add(city)
        nodes_explored += 1
        
        # Found destination
        if city == end:
            break
            
        # Check all neighbors
        for neighbor, cost in graph.get(city, {}).items():
            new_dist = dist + cost
            if new_dist < distances[neighbor]:
                distances[neighbor] = new_dist
                parent[neighbor] = city
                heapq.heappush(pq, (new_dist, neighbor))
    
    # Build path
    if end not in parent and start != end:
        return None, float('inf'), nodes_explored
    
    path = []
    current = end
    while current in parent:
        path.append(current)
        current = parent[current]
    path.append(start)
    path.reverse()
    
    return path, distances[end], nodes_explored

def analyze_results(test_results):
    """Simple analysis of Dijkstra results"""
    print("\n" + "="*50)
    print("DIJKSTRA ALGORITHM RESULTS ANALYSIS")
    print("="*50)
    
    successful = [(route, path, cost, time_ms, nodes) for route, path, cost, time_ms, nodes in test_results if path]
    
    if not successful:
        print("No successful routes found")
        return
    
    costs = [cost for _, _, cost, _, _ in successful]
    times = [time_ms for _, _, _, time_ms, _ in successful]
    nodes = [n for _, _, _, _, n in successful]
    
    print(f"Performance Summary:")
    print(f"  Routes found: {len(successful)}/{len(test_results)}")
    print(f"  Success rate: {len(successful)/len(test_results)*100:.1f}%")
    
    print(f"\nCost Analysis:")
    print(f"  Cheapest route: ₹{min(costs):.2f}")
    print(f"  Most expensive: ₹{max(costs):.2f}")
    print(f"  Average cost: ₹{sum(costs)/len(costs):.2f}")
    
    print(f"\nPerformance Metrics:")
    print(f"  Average execution time: {sum(times)/len(times):.2f}ms")
    print(f"  Average nodes explored: {sum(nodes)/len(nodes):.1f}")
    print(f"  Algorithm efficiency: {(1 - sum(nodes)/len(nodes)/15)*100:.1f}% (less exploration = better)")
    
    print(f"\nDetailed Route Results:")
    for route, path, cost, time_ms, nodes_explored in successful:
        path_str = ' → '.join(path)
        stops = len(path) - 1
        print(f"  {route}: {path_str}")
        print(f"    Cost: ₹{cost:.2f}, Stops: {stops}, Time: {time_ms:.2f}ms, Nodes: {nodes_explored}")

def explain_algorithm():
    """Explain how Dijkstra works on this dataset"""
    print("\n" + "="*50)
    print("ALGORITHM EXPLANATION")
    print("="*50)
    
    print("How Dijkstra Works Here:")
    print("1. Uses pre-discounted flight prices from Dylan's data processing")
    print("2. Finds mathematically optimal shortest path")
    print("3. Guarantees best solution for positive weights")
    print("4. Uses priority queue for efficient exploration")
    
    print("\nDiscount System Context:")
    print("- IndiGo Loyalty: 15% off IndiGo flights")
    print("- Jet Airways Loyalty: 20% off Jet Airways flights")
    print("- Credit Card Cashback: ₹1,000 off ALL airlines")
    print("- Seasonal Discount: 25% off ALL airlines")
    print("- Best discount automatically applied to each route")
    
    print("\nDijkstra's Role in Team Comparison:")
    print("✅ Provides baseline optimal paths using discounted weights")
    print("✅ Fast and reliable for positive-weight graphs")
    print("⚠️  Won't exploit multi-hop discount combinations (that's Bellman-Ford's job)")
    print("⚠️  Single objective optimization only (Dynamic Programming handles constraints)")

def main():
    """Test Dijkstra algorithm with team's sample routes"""
    print("DIJKSTRA ALGORITHM IMPLEMENTATION & ANALYSIS")
    print("Team Flight Route Optimization Project")
    print("="*60)
    
    try:
        # Load the flight data
        with open('graph_dijkstra.json', 'r') as f:
            flights = json.load(f)
        
        print(f"✅ Loaded flight graph with {len(flights)} cities")
        
        # Team's test routes from handoff document
        test_routes = [
            ('BLR', 'DEL'),  # Should find direct route ₹2,265
            ('BOM', 'HYD'),  # Should be ₹883.50 (heavily discounted)
            ('CCU', 'BOM'),  # Multi-hop opportunity for other algorithms
            ('MAA', 'AMD'),  # No direct route, requires connections
            ('DEL', 'COK'),  # Additional test case
        ]
        
        print(f"\n🧪 Testing {len(test_routes)} routes...")
        
        results = []
        for start, end in test_routes:
            start_time = time.time()
            path, cost, nodes_explored = dijkstra(flights, start, end)
            execution_time = (time.time() - start_time) * 1000  # Convert to milliseconds
            
            route_name = f"{start}→{end}"
            results.append((route_name, path, cost, execution_time, nodes_explored))
            
            if path:
                path_str = ' → '.join(path)
                print(f"  ✅ {route_name}: {path_str}, ₹{cost:.2f}")
            else:
                print(f"  ❌ {route_name}: No route found")
        
        # Analyze results
        analyze_results(results)
        
        # Explain algorithm
        explain_algorithm()
        
        # Generate comparison data for team
        print(f"\n" + "="*50)
        print("DATA FOR TEAM ALGORITHM COMPARISON")
        print("="*50)
        print("Route | Dijkstra Cost | Path | Notes")
        print("-" * 50)
        
        for route_name, path, cost, _, _ in results:
            if path:
                path_str = ' → '.join(path)
                stops = len(path) - 1
                print(f"{route_name:<8} | ₹{cost:<10.2f} | {path_str:<15} | {stops} stops")
            else:
                print(f"{route_name:<8} | {'FAILED':<10} | {'N/A':<15} | No path")
        
        print(f"\n📋 Next Steps for Team:")
        print("1. Run same routes on Bellman-Ford algorithm")
        print("2. Compare costs - Bellman-Ford may find cheaper multi-hop paths")
        print("3. Test Dynamic Programming with airline/time constraints")
        print("4. Analyze where each algorithm performs best")
        
    except FileNotFoundError:
        print("❌ Error: graph_dijkstra.json not found")
        print("Please ensure Dylan's processed data file is in the current directory")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
