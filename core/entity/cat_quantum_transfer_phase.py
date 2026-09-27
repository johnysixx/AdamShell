from enum import Enum


class CatQuantumTransferPhase(Enum):

    INACTIVE = "inactive"
    SUPERPOSITION = "cat_transfer_superposition"
    COLLAPSED = "collapsed"
    COMPLETED = "completed"
