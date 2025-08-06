from typing import Dict, List
from .models import Discount, DiscountType

# maps airport codes to full city names for lookup
CITY_CODE_TO_NAME: Dict[str, str] = {
    "DEL": "Delhi",
    "BLR": "Bangalore",
    "BOM": "Mumbai", 
    "CCU": "Kolkata",
    "MAA": "Chennai",
    "COK": "Cochin",
    "HYD": "Hyderabad",
    "PNQ": "Pune",
    "LKO": "Lucknow",
    "AMD": "Ahmedabad",
    "NAG": "Nagpur",
    "IDR": "Indore",
    "IXR": "Ranchi",
    "BBI": "Bhubaneswar",
    "GAU": "Guwahati"
}

# maps various city name formats to standardized names
CITY_NAME_MAPPINGS: Dict[str, str] = {
    "Banglore": "Bangalore",      # common misspelling
    "New Delhi": "Delhi",         # variant name
    **CITY_CODE_TO_NAME           # include all airport code mappings
}

# realistic discount scenarios automatically applied to all flights
REALISTIC_DISCOUNTS: List[Discount] = [
    # airline-specific loyalty program discounts
    Discount(
        discount_type=DiscountType.LOYALTY_PROGRAM,
        name="IndiGo Loyalty",
        percentage=15.0,                    # 15% off indigo flights
        fixed_amount=0.0,
        applicable_airlines=["IndiGo"]      # only applies to indigo
    ),
    Discount(
        discount_type=DiscountType.LOYALTY_PROGRAM,
        name="Jet Airways Loyalty", 
        percentage=20.0,                    # 20% off jet airways flights
        fixed_amount=0.0,
        applicable_airlines=["Jet Airways"] # only applies to jet airways
    ),
    # universal credit card discount
    Discount(
        discount_type=DiscountType.CREDIT_CARD,
        name="Credit Card Cashback",
        percentage=0.0,
        fixed_amount=1000.0,                # flat 1000 rupee discount
        applicable_airlines=[]              # applies to all airlines
    ),
    # universal seasonal discount (most powerful)
    Discount(
        discount_type=DiscountType.SEASONAL,
        name="Off-Peak Discount",
        percentage=25.0,                    # 25% off all flights
        fixed_amount=0.0,
        applicable_airlines=[]              # applies to all airlines
    )
]

