from enum import Enum


class CatGroupLifecycleState(Enum):

    FORMING = "forming"
    GROWING = "growing"
    STABLE = "stable"
    STRAINED = "strained"
    DISSOLVED = "dissolved"
