class DirectedActualizer:

    def __init__(
        self,
        selected_names
    ):
        self.selected_names = set(
            selected_names
        )

    def select(
        self,
        potentials
    ):
        available = [
            potential
            for potential in potentials
            if potential.is_open
            and potential.is_available
        ]

        selected = [
            potential
            for potential in available
            if potential.name
            in self.selected_names
        ]

        mandatory = [
            potential
            for potential in available
            if potential.possibility.mandatory
        ]

        for potential in mandatory:
            if potential not in selected:
                selected.append(
                    potential
                )

        if not selected:
            raise ValueError(
                "No selected potential "
                "is available."
            )

        return selected

    def actualize(
        self,
        selected
    ):
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
