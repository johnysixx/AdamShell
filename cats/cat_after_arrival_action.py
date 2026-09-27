from enum import Enum


class CatAfterArrivalAction(Enum):

    CONTINUE_EXPLORATION = "continue_exploration"
    REST_AT_DESTINATION = "rest_at_destination"
    RETURN_VIA_EXPLORATION_PAIR = (
        "return_via_exploration_pair"
    )
