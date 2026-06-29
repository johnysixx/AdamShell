from dataclasses import dataclass, field
from core.time.moment import Moment


@dataclass
class Creation:
    moment: Moment

    chaos: bool = True
    deep: bool = True
    waters: bool = True

    light: bool = False
    space: bool = False
    life: bool = False

    spirit: bool = True

    def describe(self) -> str:
        return (
            f"Creation at {self.moment.name}\n"
            f"- chaos: {self.chaos}\n"
            f"- deep: {self.deep}\n"
            f"- waters: {self.waters}\n"
            f"- light: {self.light}\n"
            f"- space: {self.space}\n"
            f"- life: {self.life}\n"
            f"- spirit: {self.spirit}"
        )