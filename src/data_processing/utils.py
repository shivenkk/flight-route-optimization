import re
from typing import Optional, Tuple, Dict, Any


# parse duration string like '2h 50m', '7h 25m', '19h' into total minutes
def parse_duration(duration_str: str) -> Optional[int]:
    # handle empty or invalid duration strings
    if not duration_str or duration_str.strip() == "":
        return None
    
    duration_str = duration_str.strip()
    
    # extract hours and minutes using regex patterns
    hours_match = re.search(r'(\d+)h', duration_str)
    minutes_match = re.search(r'(\d+)m', duration_str)
    
    # convert matches to integers or default to 0
    hours = int(hours_match.group(1)) if hours_match else 0
    minutes = int(minutes_match.group(1)) if minutes_match else 0
    
    # return total minutes
    return hours * 60 + minutes


# parse time string and normalize format
def parse_time(time_str: str) -> Optional[str]:
    # handle empty time strings
    if not time_str:
        return None
    
    time_str = time_str.strip()
    
    # extract time in HH:MM format using regex
    time_match = re.search(r'(\d{1,2}):(\d{2})', time_str)
    if time_match:
        hour = int(time_match.group(1))
        minute = int(time_match.group(2))
        # return standardized HH:MM format
        return f"{hour:02d}:{minute:02d}"
    
    return None


# normalize city name using the mapping dictionary
def normalize_city_name(city_name: str, city_mappings: Dict[str, str]) -> str:
    # handle empty city names
    if not city_name:
        return ""
    
    city_name = city_name.strip()
    
    # check if city name needs normalization
    if city_name in city_mappings:
        return city_mappings[city_name]
    
    # return original name if no mapping found
    return city_name


# validate and parse price value
def validate_price(price: Any) -> Optional[float]:
    # handle empty or null prices
    if price is None or price == "":
        return None
    
    try:
        # remove commas and convert to float
        price_float = float(str(price).replace(",", ""))
        # return only positive prices
        return price_float if price_float > 0 else None
    except (ValueError, TypeError):
        # return none for invalid price formats
        return None


# parse stops information from string
def parse_stops_info(stops_str: str) -> Tuple[str, int]:
    # handle empty stops info
    if not stops_str:
        return "non-stop", 0
    
    stops_str = stops_str.strip().lower()
    
    # parse different stop patterns
    if "non-stop" in stops_str:
        return "non-stop", 0
    elif "1 stop" in stops_str:
        return "1 stop", 1
    elif "2 stops" in stops_str:
        return "2 stops", 2
    else:
        # default to non-stop for unrecognized patterns
        return "non-stop", 0


# clean and normalize airline name
def clean_airline_name(airline: str) -> str:
    # handle empty airline names
    if not airline:
        return ""
    # remove extra whitespace
    return airline.strip()


# penalty constants for weighted price calculation
DURATION_PENALTY_PER_MINUTE = 0.05  # small penalty per minute (time has value)

# calculate weighted price for graph edges (price + time penalty)
def calculate_weighted_price(base_price: float, duration_minutes: int) -> float:
    # add small penalty to base price for duration (time has value)
    duration_penalty = duration_minutes * DURATION_PENALTY_PER_MINUTE
    
    # return total weighted cost (price + time penalty)
    return base_price + duration_penalty