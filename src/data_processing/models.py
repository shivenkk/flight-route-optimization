from dataclasses import dataclass
from typing import List
from enum import Enum


# flight stop categories for route parsing
class StopType(Enum):
    NON_STOP = "non-stop"
    ONE_STOP = "1 stop"
    TWO_STOPS = "2 stops"


# discount types available in the system
class DiscountType(Enum):
    LOYALTY_PROGRAM = "loyalty"
    CREDIT_CARD = "credit_card"
    SEASONAL = "seasonal"


# represents a city with its code and names
@dataclass
class City:
    code: str               # airport code like BLR, DEL
    name: str               # full city name like Bangalore
    normalized_name: str    # cleaned name for matching


# flight path from source to destination with stops
@dataclass
class Route:
    source: City
    destination: City
    intermediate_stops: List[City]  # cities between source and destination
    total_stops: StopType
    
    @property
    def all_cities(self) -> List[City]:
        # get complete city sequence for multi-hop routes
        return [self.source] + self.intermediate_stops + [self.destination]


# single flight record from the dataset
@dataclass
class Flight:
    airline: str            # airline name like IndiGo, SpiceJet
    date_of_journey: str    # travel date
    route: Route            # complete flight path
    departure_time: str     # departure time
    arrival_time: str       # arrival time  
    duration: str           # flight duration
    additional_info: str    # extra flight details
    base_price: float       # original price before discounts


# discount configuration with calculation logic
@dataclass
class Discount:
    discount_type: DiscountType
    name: str                           # display name like "IndiGo Loyalty"
    percentage: float                   # percentage discount amount
    fixed_amount: float                 # fixed rupee discount amount
    applicable_airlines: List[str]      # empty list means all airlines
    
    def calculate_discount(self, flight: Flight) -> float:
        # check if discount applies to this airline
        if self.applicable_airlines and flight.airline not in self.applicable_airlines:
            return 0.0
        
        # calculate total discount from percentage + fixed amount
        percentage_discount = flight.base_price * (self.percentage / 100)
        total_discount = percentage_discount + self.fixed_amount
        
        # cap discount at 50% to prevent negative prices
        max_discount = flight.base_price * 0.5
        return min(total_discount, max_discount)


# flight after discount processing is complete
@dataclass
class ProcessedFlight:
    original_flight: Flight    # original flight data
    final_price: float         # price after best discount applied