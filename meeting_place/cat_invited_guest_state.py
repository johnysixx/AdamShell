from dataclasses import dataclass


@dataclass(slots=True)
class CatInvitedGuestState:
    human: str
    inviting_cat: str
    invitation_id: str
    cat_present: bool = True
    entered_together: bool = True
    permanent_access: bool = False
