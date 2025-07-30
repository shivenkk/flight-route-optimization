#!/usr/bin/env python3
# simple flight data processing script
# loads csv, cleans data, builds graph, exports 3 formats for algorithms

import os
import sys
import pandas as pd

# Add src to Python path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from data_processing.data_processor import FlightDataCleaner, RouteParser, DiscountEngine
from data_processing.graph_builder import FlightGraph, GraphExporter
from data_processing.config import REALISTIC_DISCOUNTS


def main():
    # check command line arguments
    if len(sys.argv) != 2:
        print("Usage: python process_data.py <input_csv_file>")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_dir = "output"
    
    # validate input file exists
    if not os.path.exists(input_file):
        print(f"Error: Input file '{input_file}' not found")
        sys.exit(1)
    
    # create output directory if needed
    os.makedirs(output_dir, exist_ok=True)
    
    # step 1: load raw csv data
    print("Loading flight data...")
    df = pd.read_csv(input_file)
    
    # step 2: clean and normalize the data
    print("Cleaning flight data...")
    cleaner = FlightDataCleaner()
    cleaned_df, _ = cleaner.clean_dataset(df)
    
    # step 3: convert dataframe rows to flight objects
    print("Parsing flight routes...")
    parser = RouteParser()
    flights = parser.convert_to_flight_objects(cleaned_df)
    
    # step 4: apply realistic discounts to all flights
    print("Applying discounts...")
    discount_engine = DiscountEngine(REALISTIC_DISCOUNTS)
    processed_flights = discount_engine.apply_discounts(flights)
    
    # step 5: build graph structure from processed flights
    print("Building flight graph...")
    flight_graph = FlightGraph()
    flight_graph.add_flights(processed_flights)
    
    # step 6: export in the 3 formats needed by algorithms
    print("Exporting graph data...")
    exporter = GraphExporter(flight_graph)
    
    # adjacency list format for dijkstra
    exporter.export_for_dijkstra(os.path.join(output_dir, "graph_dijkstra.json"))
    # edge list format for bellman-ford  
    exporter.export_for_bellman_ford(os.path.join(output_dir, "graph_bellman_ford.json"))
    # detailed edge data for dynamic programming
    exporter.export_edge_list(os.path.join(output_dir, "graph_edge_list.json"))
    
    print(f"Processing complete! Files saved to: {output_dir}")


if __name__ == "__main__":
    main()