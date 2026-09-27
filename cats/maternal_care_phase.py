from enum import Enum


class MaternalCarePhase(Enum):

    NEONATAL = "neonatal_maternal_care"
    COMPLETE = "complete_maternal_care"
    REDUCED = "reduced_maternal_care"
    INDEPENDENCE = "maternal_independence"
