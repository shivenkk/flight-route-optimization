"""
Dynamic Programming Algorithm Implementation for Flight Route Optimization
The graph data is available in: ../../output/graph_edge_list.json
Format: [{"source": "...", "destination": "...", "weight": ..., "price": ..., "airline": ..., ...}, ...]
"""
import json
from collections import defaultdict

def load_edge_data(filepath='output/graph_edge_list.json'):
    with open(filepath, 'r') as f:
        return json.load(f)

def build_graph_from_edges(edges):
    graph = defaultdict(list)
    cities = set()
    
    for edge in edges:
        graph[edge['source']].append(edge)
        cities.add(edge['source'])
        cities.add(edge['destination'])
    
    return graph, sorted(list(cities))

def dp_shortest_path(edges, start, end, constraints=None):
    # Build the graph
    graph, cities = build_graph_from_edges(edges)
    
    if constraints is None:
        constraints = {}
    
    # Get constraints
    max_stops = constraints.get('max_stops', len(cities))
    max_duration = constraints.get('max_duration', float('inf'))
    budget = constraints.get('budget', float('inf'))
    preferred_airlines = set(constraints.get('preferred_airlines', []))
    avoid_airlines = set(constraints.get('avoid_airlines', []))
    
    # DP table: dp[city][stops_used] = (cost, duration, path, details)
    dp = defaultdict(lambda: defaultdict(lambda: (float('inf'), 0, [], [])))
    
    # Start with source city
    dp[start][0] = (0, 0, [start], [])
    
    # Build up the DP table
    for stops in range(max_stops + 1):
        for city in cities:
            if dp[city][stops][0] == float('inf'):
                continue
            
            current_cost, current_duration, current_path, current_details = dp[city][stops]
            
            # Try all flights from this city
            for flight in graph[city]:
                dest = flight['destination']
                airline = flight['airline']
                
                # Skip if we should avoid this airline
                if airline in avoid_airlines:
                    continue
                
                # Calculate cost with preference penalty
                flight_cost = flight['weight']
                if preferred_airlines and airline not in preferred_airlines:
                    flight_cost *= 1.15  # 15% penalty for non-preferred airlines
                
                new_cost = current_cost + flight_cost
                new_duration = current_duration + flight['duration_minutes']
                
                # Check if this violates constraints
                if new_cost > budget or new_duration > max_duration:
                    continue
                
                # Update if we found a better path
                if new_cost < dp[dest][stops + 1][0]:
                    new_path = current_path + [dest]
                    new_details = current_details + [{
                        'from': city,
                        'to': dest,
                        'airline': airline,
                        'cost': flight['weight'],
                        'original_price': flight['price'],
                        'duration': flight['duration_minutes']
                    }]
                    dp[dest][stops + 1] = (new_cost, new_duration, new_path, new_details)
    
    # Find best path to destination
    best_cost = float('inf')
    best_result = None
    
    for stops in range(max_stops + 1):
        if dp[end][stops][0] < best_cost:
            best_cost = dp[end][stops][0]
            cost, duration, path, details = dp[end][stops]
            best_result = {
                'path': path,
                'total_cost': cost,
                'total_duration': duration,
                'total_stops': len(path) - 2,
                'flights': details,
                'algorithm': 'Dynamic Programming'
            }
    
    if best_result is None:
        return {
            'path': None,
            'total_cost': float('inf'),
            'error': f'No path found from {start} to {end} with given constraints',
            'algorithm': 'Dynamic Programming'
        }
    
    return best_result

def print_route(result):
    if result['path'] is None:
        print(result['error'])
        return
    
    print(f"Route: {' → '.join(result['path'])}")
    print(f"Total Cost: ₹{result['total_cost']:.2f}")
    print(f"Total Duration: {result['total_duration']} min ({result['total_duration']//60}h {result['total_duration']%60}m)")
    print(f"Total Stops: {result['total_stops']}")
    
    if result.get('flights'):
        print("\nFlight Details:")
        for i, flight in enumerate(result['flights'], 1):
            print(f"  {i}. {flight['from']} → {flight['to']}")
            print(f"     Airline: {flight['airline']}")
            print(f"     Cost: ₹{flight['cost']:.2f}")
            print(f"     Duration: {flight['duration']} min")

# Testing
if __name__ == "__main__":
    edges = load_edge_data()
    print(f"Loaded {len(edges)} flights\n")
    
    # Test basic path
    print("Test 1: BLR to DEL")
    print("-" * 40)
    result = dp_shortest_path(edges, 'BLR', 'DEL')
    print_route(result)
    
    # Test with constraints
    print("\n\nTest 2: BLR to DEL (max 1 stop)")
    print("-" * 40)
    result = dp_shortest_path(edges, 'BLR', 'DEL', {'max_stops': 1})
    print_route(result)
    
    # Test airline preference
    print("\n\nTest 3: CCU to BOM (prefer IndiGo)")
    print("-" * 40)
    result = dp_shortest_path(edges, 'CCU', 'BOM', {
        'preferred_airlines': ['IndiGo'],
        'max_stops': 2
    })
    print_route(result)
    
    # Test budget constraint
    print("\n\nTest 4: MAA to AMD (budget ₹5000)")
    print("-" * 40)
    result = dp_shortest_path(edges, 'MAA', 'AMD', {
        'budget': 5000,
        'max_duration': 300,
        'max_stops': 2
    })
    print_route(result)
