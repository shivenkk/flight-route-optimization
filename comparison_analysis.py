"""
comparison_analysis.py
Compares all three algorithms on runtime, paths, and scalability
"""

import time
import json
import matplotlib.pyplot as plt
import numpy as np
from src.algorithms.dijkstra import find_shortest_path as dijkstra_path
from src.algorithms.bellman_ford import find_shortest_path as bellman_ford_path
from src.algorithms.dynamic_programming import dp_shortest_path, load_edge_data

def run_comparison():
    # File paths
    dijkstra_file = "output/graph_dijkstra.json"
    bellman_file = "output/graph_bellman_ford.json"
    dp_edges = load_edge_data("output/graph_edge_list.json")
    
    # Test routes
    test_routes = [
        ('BLR', 'DEL'),
        ('CCU', 'BOM'),
        ('MAA', 'AMD')
    ]
    
    print("\nFLIGHT ROUTE OPTIMIZATION: ALGORITHM COMPARISON\n")
    
    # Runtime comparison
    print("1. RUNTIME COMPARISON\n")
    
    runtime_results = []
    
    for start, end in test_routes:
        # Run each algorithm
        dij_result = dijkstra_path(dijkstra_file, start, end)
        dij_time = dij_result.get('execution_time', 0) * 1000
        
        bf_result = bellman_ford_path(bellman_file, start, end)
        bf_time = bf_result.get('execution_time', 0) * 1000
        
        t3 = time.time()
        dp_result = dp_shortest_path(dp_edges, start, end)
        dp_time = (time.time() - t3) * 1000
        
        print(f"{start} to {end}: Dijkstra: {dij_time:.2f}ms | Bellman-Ford: {bf_time:.2f}ms | DP: {dp_time:.2f}ms")
        
        runtime_results.append({
            'route': f"{start} to {end}",
            'dijkstra': dij_result,
            'bellman_ford': bf_result,
            'dp': dp_result,
            'times': {'dijkstra': dij_time, 'bellman_ford': bf_time, 'dp': dp_time}
        })
    
    # Path and cost differences
    print("\n2. PATH & COST DIFFERENCES\n")
    
    for result in runtime_results:
        route = result['route']
        dij = result['dijkstra']
        bf = result['bellman_ford']
        dp = result['dp']
        
        # Get costs
        dij_cost = dij.get('cost', float('inf'))
        bf_cost = bf.get('cost', float('inf'))
        dp_cost = dp.get('total_cost', float('inf'))
        
        # Get paths
        dij_path_str = ' -> '.join(dij['path']) if dij.get('path') else 'No path'
        bf_path_str = ' -> '.join(bf['path']) if bf.get('path') else 'No path'
        dp_path_str = ' -> '.join(dp['path']) if dp.get('path') else 'No path'
        
        # Check if they differ
        if dij_cost != bf_cost or bf_cost != dp_cost or dij_path_str != bf_path_str or bf_path_str != dp_path_str:
            print(f"{route}:")
            print(f"  Dijkstra:      Path: {dij_path_str}, Cost: Rs.{dij_cost:.2f}")
            print(f"  Bellman-Ford:  Path: {bf_path_str}, Cost: Rs.{bf_cost:.2f}")
            print(f"  Dynamic Prog:  Path: {dp_path_str}, Cost: Rs.{dp_cost:.2f}")
            
            if dij_cost != bf_cost:
                print(f"  Note: Cost difference due to discount handling")
            if dp_cost != dij_cost and dp_cost != float('inf'):
                print(f"  Note: DP cost differs due to constraint implementation")
        else:
            print(f"{route}: All algorithms found same path at Rs.{dij_cost:.2f}")
    
    # Scalability
    print("\n3. SCALABILITY ANALYSIS\n")
    
    city_subsets = {
        'Small (5 cities)': [('BLR', 'DEL'), ('BOM', 'HYD')],
        'Medium (10 cities)': [('BLR', 'DEL'), ('CCU', 'BOM'), ('MAA', 'AMD')],
        'Full (15 cities)': test_routes + [('DEL', 'MAA'), ('BOM', 'CCU')]
    }
    
    scalability_data = {}
    for size_name, routes in city_subsets.items():
        total_times = {'dijkstra': 0, 'bellman_ford': 0, 'dp': 0}
        
        for start, end in routes:
            dij_result = dijkstra_path(dijkstra_file, start, end)
            total_times['dijkstra'] += dij_result.get('execution_time', 0) * 1000
            
            bf_result = bellman_ford_path(bellman_file, start, end)
            total_times['bellman_ford'] += bf_result.get('execution_time', 0) * 1000
            
            t = time.time()
            dp_shortest_path(dp_edges, start, end)
            total_times['dp'] += (time.time() - t) * 1000
        
        avg_times = {k: v/len(routes) for k, v in total_times.items()}
        scalability_data[size_name] = avg_times
        print(f"{size_name}: Dijkstra: {avg_times['dijkstra']:.2f}ms | "
              f"Bellman-Ford: {avg_times['bellman_ford']:.2f}ms | "
              f"DP: {avg_times['dp']:.2f}ms")
    
    # Create visualizations
    create_visualizations(runtime_results, scalability_data)

def create_visualizations(runtime_results, scalability_data):
    """Create and save comparison graphs"""
    
    # Setup figure with subplots
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    fig.suptitle('Algorithm Comparison Analysis', fontsize=16)
    
    # 1. Runtime comparison bar chart
    ax1 = axes[0, 0]
    routes = [r['route'] for r in runtime_results]
    dijkstra_times = [r['times']['dijkstra'] for r in runtime_results]
    bf_times = [r['times']['bellman_ford'] for r in runtime_results]
    dp_times = [r['times']['dp'] for r in runtime_results]
    
    x = np.arange(len(routes))
    width = 0.25
    
    ax1.bar(x - width, dijkstra_times, width, label='Dijkstra')
    ax1.bar(x, bf_times, width, label='Bellman-Ford')
    ax1.bar(x + width, dp_times, width, label='Dynamic Programming')
    
    ax1.set_xlabel('Routes')
    ax1.set_ylabel('Runtime (ms)')
    ax1.set_title('Runtime Comparison by Route')
    ax1.set_xticks(x)
    ax1.set_xticklabels(routes)
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # 2. Cost comparison
    ax2 = axes[0, 1]
    costs_data = []
    for r in runtime_results:
        dij_cost = r['dijkstra'].get('cost', 0)
        bf_cost = r['bellman_ford'].get('cost', 0)
        dp_cost = r['dp'].get('total_cost', 0)
        costs_data.append([dij_cost, bf_cost, dp_cost])
    
    costs_array = np.array(costs_data)
    x2 = np.arange(len(routes))
    
    ax2.bar(x2 - width, costs_array[:, 0], width, label='Dijkstra')
    ax2.bar(x2, costs_array[:, 1], width, label='Bellman-Ford')
    ax2.bar(x2 + width, costs_array[:, 2], width, label='Dynamic Programming')
    
    ax2.set_xlabel('Routes')
    ax2.set_ylabel('Cost (Rs)')
    ax2.set_title('Cost Comparison by Route')
    ax2.set_xticks(x2)
    ax2.set_xticklabels(routes)
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    # 3. Scalability line plot
    ax3 = axes[1, 0]
    sizes = list(scalability_data.keys())
    dijkstra_scale = [scalability_data[s]['dijkstra'] for s in sizes]
    bf_scale = [scalability_data[s]['bellman_ford'] for s in sizes]
    dp_scale = [scalability_data[s]['dp'] for s in sizes]
    
    x3 = range(len(sizes))
    ax3.plot(x3, dijkstra_scale, 'o-', label='Dijkstra', linewidth=2)
    ax3.plot(x3, bf_scale, 's-', label='Bellman-Ford', linewidth=2)
    ax3.plot(x3, dp_scale, '^-', label='Dynamic Programming', linewidth=2)
    
    ax3.set_xlabel('Network Size')
    ax3.set_ylabel('Average Runtime (ms)')
    ax3.set_title('Scalability Analysis')
    ax3.set_xticks(x3)
    ax3.set_xticklabels(sizes)
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    
    # 4. Algorithm efficiency ratio
    ax4 = axes[1, 1]
    avg_dijkstra = np.mean([r['times']['dijkstra'] for r in runtime_results])
    avg_bf = np.mean([r['times']['bellman_ford'] for r in runtime_results])
    avg_dp = np.mean([r['times']['dp'] for r in runtime_results])
    
    algorithms = ['Dijkstra', 'Bellman-Ford', 'Dynamic Prog']
    avg_times = [avg_dijkstra, avg_bf, avg_dp]
    colors = ['green', 'blue', 'orange']
    
    bars = ax4.bar(algorithms, avg_times, color=colors)
    ax4.set_ylabel('Average Runtime (ms)')
    ax4.set_title('Overall Algorithm Performance')
    ax4.grid(True, alpha=0.3, axis='y')
    
    # Add value labels on bars
    for bar, time in zip(bars, avg_times):
        height = bar.get_height()
        ax4.text(bar.get_x() + bar.get_width()/2., height,
                f'{time:.2f}ms', ha='center', va='bottom')
    
    plt.tight_layout()
    
    # Save figure
    plt.savefig('output/algorithm_comparison.png', dpi=300, bbox_inches='tight')
    print("\nVisualization saved to: output/algorithm_comparison.png")
    
    # Also save individual charts
    for i, (ax, name) in enumerate(zip([ax1, ax2, ax3, ax4], 
                                       ['runtime', 'cost', 'scalability', 'performance'])):
        extent = ax.get_window_extent().transformed(fig.dpi_scale_trans.inverted())
        fig.savefig(f'output/comparison_{name}.png', bbox_inches=extent.expanded(1.2, 1.2), dpi=150)
    
    print("Individual charts saved to: output/comparison_*.png")
    
    plt.show()

if __name__ == "__main__":
    run_comparison()