import re
from typing import List, Dict, Tuple
import pandas as pd
from .models import Flight, City, Route, StopType, Discount, ProcessedFlight
from .utils import (
    normalize_city_name, validate_price, parse_duration, parse_time,
    parse_stops_info, clean_airline_name
)
from .config import CITY_NAME_MAPPINGS, CITY_CODE_TO_NAME


# cleans and validates raw csv flight data
class FlightDataCleaner:
    
    def __init__(self, city_mappings: Dict[str, str] = None):
        # use provided mappings or default ones from config
        self.city_mappings = city_mappings or CITY_NAME_MAPPINGS
        
    # clean entire dataset and return cleaned data with validation errors
    def clean_dataset(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, List[str]]:
        errors = []
        cleaned_df = df.copy()
        
        print(f"Processing {len(cleaned_df)} flight records...")
        
        # clean airline names to remove extra spaces and standardize
        cleaned_df['Airline'] = cleaned_df['Airline'].apply(clean_airline_name)
        
        # normalize city names using our mapping dictionary
        cleaned_df['Source'] = cleaned_df['Source'].apply(
            lambda x: normalize_city_name(str(x), self.city_mappings)
        )
        cleaned_df['Destination'] = cleaned_df['Destination'].apply(
            lambda x: normalize_city_name(str(x), self.city_mappings)
        )
        
        # parse price strings into clean float values
        cleaned_df['Cleaned_Price'] = cleaned_df['Price'].apply(validate_price)
        
        # convert duration strings like "2h 30m" to total minutes
        cleaned_df['Duration_Minutes'] = cleaned_df['Duration'].apply(
            lambda x: parse_duration(str(x))
        )
        
        # clean time formats for departure and arrival
        cleaned_df['Departure_Time_Clean'] = cleaned_df['Dep_Time'].apply(
            lambda x: parse_time(str(x))
        )
        cleaned_df['Arrival_Time_Clean'] = cleaned_df['Arrival_Time'].apply(
            lambda x: parse_time(str(x))
        )
        
        # parse stop information into normalized format and count
        cleaned_df[['Stops_Normalized', 'Stops_Count']] = cleaned_df['Total_Stops'].apply(
            lambda x: pd.Series(parse_stops_info(str(x)))
        )
        
        # basic validation - flag unusually expensive flights
        high_price_mask = cleaned_df['Cleaned_Price'] > 50000
        high_price_count = high_price_mask.sum()
        if high_price_count > 0:
            errors.extend([f"Found {high_price_count} flights with prices above ₹50,000"])
        
        # create mask for valid flight records
        valid_mask = (
            cleaned_df['Cleaned_Price'].notna() &           # has valid price
            cleaned_df['Duration_Minutes'].notna() &        # has valid duration
            (cleaned_df['Source'] != cleaned_df['Destination']) &  # different cities
            (cleaned_df['Source'] != '') &                  # source not empty
            (cleaned_df['Destination'] != '')               # destination not empty
        )
        
        # filter out invalid records and report count
        invalid_count = len(cleaned_df) - valid_mask.sum()
        if invalid_count > 0:
            print(f"Filtered out {invalid_count} invalid records")
        
        cleaned_df = cleaned_df[valid_mask].reset_index(drop=True)
        
        print(f"Successfully cleaned {len(cleaned_df)} flight records")
        return cleaned_df, errors


# parses flight route strings and creates route objects
class RouteParser:
    
    def __init__(self, city_mappings: Dict[str, str] = None):
        # use provided mappings or default ones from config
        self.city_mappings = city_mappings or CITY_NAME_MAPPINGS
        self.city_codes = CITY_CODE_TO_NAME
        
    # parse route string to extract intermediate stops
    def parse_route_string(self, route_str: str) -> List[str]:
        # handle empty or missing route strings
        if not route_str or route_str.strip() == "":
            return []
        
        route_str = route_str.strip()
        
        # split on common route separators like → > -
        parts = re.split(r'[→>-]', route_str)
        parts = [part.strip() for part in parts if part.strip()]
        
        # need at least 3 parts for intermediate stops (source → stop → destination)
        if len(parts) <= 2:
            return []
        
        # extract intermediate cities (exclude first and last)
        intermediate_codes = parts[1:-1]
        
        # filter to only valid city codes from our mapping
        return [code for code in intermediate_codes if code in self.city_codes]
    
    # create a city object from city name or code
    def create_city_object(self, city_identifier: str) -> City:
        # normalize the city name first
        normalized_name = normalize_city_name(city_identifier, self.city_mappings)
        
        # check if input is already a city code
        if city_identifier in self.city_codes:
            code = city_identifier
            name = self.city_codes[city_identifier]
        else:
            # treat as city name and look up code
            name = normalized_name
            code = self._get_city_code(name)
        
        return City(
            code=code,
            name=name,
            normalized_name=normalized_name
        )
    
    # look up airport code by matching city name
    def _get_city_code(self, city_name: str) -> str:
        # look up airport code by matching city name
        for code, name in self.city_codes.items():
            if name.lower() == city_name.lower():
                return code
        # fallback: use first 3 letters of city name as code
        return city_name[:3].upper()
    
    # parse complete route information from a flight record
    def parse_flight_route(self, row: pd.Series) -> Route:
        # create city objects for source and destination
        source_city = self.create_city_object(str(row['Source']))
        dest_city = self.create_city_object(str(row['Destination']))
        
        # parse intermediate stops if route string exists
        intermediate_codes = []
        if 'Route' in row and pd.notna(row['Route']):
            intermediate_codes = self.parse_route_string(str(row['Route']))
        
        # convert intermediate codes to city objects
        intermediate_cities = [
            self.create_city_object(code) for code in intermediate_codes
        ]
        
        # map stop strings to enum values
        stop_type_map = {
            "non-stop": StopType.NON_STOP,
            "1 stop": StopType.ONE_STOP,
            "2 stops": StopType.TWO_STOPS
        }
        
        stops_str = str(row.get('Stops_Normalized', 'non-stop'))
        stop_type = stop_type_map.get(stops_str, StopType.NON_STOP)
        
        return Route(
            source=source_city,
            destination=dest_city,
            intermediate_stops=intermediate_cities,
            total_stops=stop_type
        )
    
    # convert cleaned dataframe to flight objects
    def convert_to_flight_objects(self, cleaned_df: pd.DataFrame) -> List[Flight]:
        flights = []
        
        # process each row in the cleaned dataframe
        for _, row in cleaned_df.iterrows():
            try:
                # parse the route information
                route = self.parse_flight_route(row)
                
                # create flight object with all fields
                flight = Flight(
                    airline=str(row['Airline']),
                    date_of_journey=str(row['Date_of_Journey']),
                    route=route,
                    departure_time=str(row.get('Departure_Time_Clean', row['Dep_Time'])),
                    arrival_time=str(row.get('Arrival_Time_Clean', row['Arrival_Time'])),
                    duration=str(row['Duration']),
                    additional_info=str(row.get('Additional_Info', '')),
                    base_price=float(row['Cleaned_Price'])
                )
                
                flights.append(flight)
                
            except Exception as e:
                # skip problematic records and continue processing
                print(f"Error creating flight object: {e}")
                continue
        
        print(f"Successfully created {len(flights)} Flight objects")
        return flights


# applies discount rules to flights and finds best deals
class DiscountEngine:
    
    def __init__(self, available_discounts: List[Discount]):
        # store list of all available discounts from config
        self.available_discounts = available_discounts
    
    # apply discounts to flights and return processed flights
    def apply_discounts(self, flights: List[Flight]) -> List[ProcessedFlight]:
        processed_flights = []
        discount_count = 0
        
        # process each flight and find best applicable discount
        for flight in flights:
            # check all available discounts and find the best one
            best_discount = 0.0
            for discount in self.available_discounts:
                discount_amount = discount.calculate_discount(flight)
                if discount_amount > best_discount:
                    best_discount = discount_amount
            
            # apply best discount but keep minimum 50% of original price
            final_price = max(flight.base_price * 0.5, flight.base_price - best_discount)
            
            # track how many flights got discounts
            if best_discount > 0:
                discount_count += 1
            
            # create processed flight with final discounted price
            processed_flight = ProcessedFlight(
                original_flight=flight,
                final_price=final_price
            )
            processed_flights.append(processed_flight)
        
        print(f"Applied discounts to {discount_count} flights")
        return processed_flights
    
    # generate simple discount statistics
    def get_discount_summary(self, processed_flights: List[ProcessedFlight]) -> Dict[str, any]:
        total_flights = len(processed_flights)
        
        # count flights that got discounts (final price < original price)
        flights_with_discounts = sum(1 for pf in processed_flights 
                                   if pf.final_price < pf.original_flight.base_price)
        
        # calculate total savings across all flights
        total_savings = sum(pf.original_flight.base_price - pf.final_price 
                          for pf in processed_flights)
        avg_savings = total_savings / total_flights if total_flights > 0 else 0
        
        # return summary statistics
        return {
            'total_flights': total_flights,
            'flights_with_discounts': flights_with_discounts,
            'discount_application_rate': flights_with_discounts / total_flights * 100,
            'total_savings': total_savings,
            'average_savings_per_flight': avg_savings
        }