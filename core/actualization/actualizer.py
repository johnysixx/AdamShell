class Actualizer:

    def __init__(self, rng=None):
        if rng is None:
            import random
            rng = random

        self.rng = rng

    def select(self, potentials):
        available = [
            potential
            for potential in potentials
            if potential.is_open
            and potential.is_available
        ]

        if not available:
            raise RuntimeError(
                "Actualization requires at least "
                "one available potential."
            )

        selected = []

        for potential in available:
            if potential.possibility.mandatory:
                selected.append(
                    potential
                )
                continue

            if (
                self.rng.random()
                <= potential.possibility.probability
            ):
                selected.append(
                    potential
                )

        if not selected:
            selected.append(
                self.rng.choice(
                    available
                )
            )

        return selected

    def actualize(self, selected):
        events = []

        for potential in selected:
            if not potential.is_open:
                continue

            event = (
                potential.possibility.actualize()
            )

            potential.mark_actualized()

            events.append(
                event
            )

        return events
