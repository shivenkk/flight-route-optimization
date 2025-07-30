import networkx as nx
import json
from typing import List, Dict
from .models import ProcessedFlight, City
from .utils import calculate_weighted_price


# builds networkx graph from processed flight data
class FlightGraph:
    
    def __init__(self):
        # directed graph since flights have specific directions
        self.graph = nx.DiGraph()
        self.city_nodes: Dict[str, City] = {}       # city code -> city object mapping
        self.flight_edges: List[ProcessedFlight] = []  # store all flight data
        
    # add processed flights to the graph
    def add_flights(self, processed_flights: List[ProcessedFlight]) -> None:
        print(f"Building graph from {len(processed_flights)} flights...")
        
        # add each flight as nodes and edges in the graph
        for processed_flight in processed_flights:
            self._add_flight_to_graph(processed_flight)
        
        # store flights for later export operations
        self.flight_edges = processed_flights
        
        print(f"Graph built with {self.graph.number_of_nodes()} cities and {self.graph.number_of_edges()} direct routes")
    
    # add a single flight to the graph
    def _add_flight_to_graph(self, processed_flight: ProcessedFlight) -> None:
        flight = processed_flight.original_flight
        route = flight.route
        
        # add all cities as nodes first
        self._add_city_node(route.source)
        self._add_city_node(route.destination)
        
        # add intermediate stops as nodes too
        for intermediate_city in route.intermediate_stops:
            self._add_city_node(intermediate_city)
        
        # create edges between consecutive cities in the route
        all_cities = route.all_cities
        for i in range(len(all_cities) - 1):
            source_city = all_cities[i]
            dest_city = all_cities[i + 1]
            
            # add edge with flight data (first segment gets full flight info)
            self._add_flight_edge(source_city, dest_city, processed_flight, i == 0)
    
    # add a city as a node in the graph
    def _add_city_node(self, city: City) -> None:
        # only add if not already present
        if city.code not in self.city_nodes:
            self.city_nodes[city.code] = city
            self.graph.add_node(
                city.code,
                name=city.name,
                normalized_name=city.normalized_name,
                city_object=city
            )
    
    # add a flight edge between two cities
    def _add_flight_edge(self, source: City, destination: City, 
                        processed_flight: ProcessedFlight, is_primary_segment: bool) -> None:
        flight = processed_flight.original_flight
        
        # parse duration string to minutes
        duration_minutes = 0
        if hasattr(flight, 'duration') and flight.duration:
            from .utils import parse_duration
            duration_minutes = parse_duration(flight.duration) or 0
        
        # count intermediate stops for this route
        num_stops = len(flight.route.intermediate_stops)
        
        # calculate weighted price considering duration and stops
        weight = calculate_weighted_price(
            processed_flight.final_price,
            duration_minutes,
            num_stops
        )
        
        # package all edge attributes for algorithms
        edge_data = {
            'weight': weight,                           # final weight for algorithms
            'price': processed_flight.final_price,     # discounted price
            'base_price': flight.base_price,           # original price
            'airline': flight.airline,                 # airline name
            'duration_minutes': duration_minutes,      # flight duration
            'stops': num_stops,                        # number of stops
            'flight_object': processed_flight,         # full flight data
            'is_primary_segment': is_primary_segment   # true for main route segment
        }
        
        # keep only the cheapest flight between each city pair
        if self.graph.has_edge(source.code, destination.code):
            existing_weight = self.graph[source.code][destination.code]['weight']
            # replace if this flight is cheaper
            if weight < existing_weight:
                self.graph.add_edge(source.code, destination.code, **edge_data)
        else:
            # first flight between these cities
            self.graph.add_edge(source.code, destination.code, **edge_data)
    


# exports graph data in 3 formats for different algorithms
class GraphExporter:
    
    def __init__(self, flight_graph: FlightGraph):
        # store references to the graph data
        self.flight_graph = flight_graph
        self.graph = flight_graph.graph
    
    # export for dijkstra's algorithm: {source: {destination: weight}}
    def export_for_dijkstra(self, output_file: str) -> None:
        dijkstra_graph = {}
        
        # initialize empty adjacency list for each city
        for node in self.graph.nodes():
            dijkstra_graph[node] = {}
        
        # add edges with weights to adjacency list format
        for source, dest, data in self.graph.edges(data=True):
            dijkstra_graph[source][dest] = data['weight']
        
        # save as json file
        with open(output_file, 'w') as f:
            json.dump(dijkstra_graph, f, indent=2)
    
    # export for bellman-ford algorithm: {nodes: [...], edges: [[source, dest, weight], ...]}
    def export_for_bellman_ford(self, output_file: str) -> None:
        # get all city nodes as a list
        nodes = list(self.graph.nodes())
        # convert edges to [source, destination, weight] format
        edges = [[source, dest, data['weight']] for source, dest, data in self.graph.edges(data=True)]
        
        # package in bellman-ford expected format
        result = {'nodes': nodes, 'edges': edges}
        
        # save as json file
        with open(output_file, 'w') as f:
            json.dump(result, f, indent=2)
    
    # export detailed edge list for dynamic programming with constraints
    def export_edge_list(self, output_file: str) -> None:
        edges = []
        
        # create detailed edge objects with all constraint data
        for source, dest, data in self.graph.edges(data=True):
            edge = {
                'source': source,
                'destination': dest,
                'weight': data['weight'],              # final discounted weight
                'price': data['price'],               # discounted price
                'airline': data['airline'],           # airline name
                'duration_minutes': data['duration_minutes'],  # flight duration
                'stops': data['stops']                # number of stops
            }
            edges.append(edge)
        
        # save as json array
        with open(output_file, 'w') as f:
            json.dump(edges, f, indent=2)