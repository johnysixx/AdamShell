from dataclasses import dataclass


@dataclass
class UniverseState:
    exists: bool = True

    light: bool = False
    time: bool = False
    space: bool = False
    life: bool = False

    chaos: bool = True
    deep: bool = True
    waters: bool = True

    spirit_hovering: bool = True