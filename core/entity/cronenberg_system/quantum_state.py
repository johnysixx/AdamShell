from dataclasses import dataclass


@dataclass(slots=True)
class CronenbergQuantumState:

    spin: float = 0.5
    entangled: bool = False
    pair_id: str | None = None
    counterpart_id: str | None = None
    counterpart_potential: bool = True
    counterpart_manifested: bool = False

    def pair_with(
        self,
        pair_id,
        counterpart_id,
        spin=None,
    ):
        if spin is not None:
            self.spin = float(spin)

        self.entangled = True
        self.pair_id = str(pair_id)
        self.counterpart_id = str(
            counterpart_id
        )
        self.counterpart_potential = True
        self.counterpart_manifested = True

    def disentangle(self):
        self.entangled = False

    def reset(self, spin=0.0):
        self.spin = float(spin)
        self.entangled = False
        self.pair_id = None
        self.counterpart_id = None
        self.counterpart_potential = True
        self.counterpart_manifested = False

    def to_dict(self):
        return {
            "spin": self.spin,
            "entangled": self.entangled,
            "pair_id": self.pair_id,
            "counterpart_id": (
                self.counterpart_id
            ),
            "counterpart_potential": (
                self.counterpart_potential
            ),
            "counterpart_manifested": (
                self.counterpart_manifested
            ),
        }
