from enum import Enum


class BouncerState(Enum):

    STANDING_OUTSIDE_BAR = "standing_outside_bar"
    RESPONDING_INSIDE_BAR = "responding_inside_bar"
    INSIDE_AND_OUTSIDE_BAR = "inside_and_outside_bar"
