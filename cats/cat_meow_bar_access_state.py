from dataclasses import dataclass


@dataclass(slots=True)
class CatMeowBarAccessState:
    source: str
    inviting_cat: str
    invitation_id: str
    permanent: bool = False
