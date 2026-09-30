from enum import Enum


class GodBookLibraryStatus(Enum):

    UNREGISTERED = "unregistered"
    SHELVED = "shelved"
    CHECKED_OUT_FOR_EDIT = "checked_out_for_edit"
