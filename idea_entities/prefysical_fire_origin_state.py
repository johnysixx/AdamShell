from enum import Enum


class PrefysicalFireOriginState(Enum):

    PREPARED = "prepared"
    SEEKING_WARMTH = "seeking_warmth"
    FIRE_BURNING = "fire_burning"
    FIRE_GUARDED_FUEL_SEARCH_ACTIVE = (
        "fire_guarded_fuel_search_active"
    )
