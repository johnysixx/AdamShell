from dataclasses import dataclass

from cats.cat_door import CatDoor


@dataclass(slots=True, frozen=True)
class CatDoorPair:
    forward: CatDoor
    backward: CatDoor

    def __post_init__(self):
        if not isinstance(
            self.forward,
            CatDoor,
        ):
            raise TypeError(
                "Cat door pair forward door "
                "must be a CatDoor object."
            )

        if not isinstance(
            self.backward,
            CatDoor,
        ):
            raise TypeError(
                "Cat door pair backward door "
                "must be a CatDoor object."
            )
