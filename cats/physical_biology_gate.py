class PhysicalBiologyGate:

    def __init__(
        self,
        universe
    ):
        self.universe = universe
        self.history = []

    def require_physical_world(
        self,
        operation,
        cat=None
    ):
        if getattr(
            self.universe,
            "physical_universe_started",
            False
        ):
            return {
                "allowed": True,
                "operation": operation,
                "cronenberg": None
            }

        cat_name = (
            cat.get("name")
            if isinstance(cat, dict)
            else None
        )

        cronenberg = (
            self.universe
            .create_cronenberg_from_quantum_error(
                error=RuntimeError(
                    "Biological cat process attempted "
                    "before the physical universe existed."
                ),
                source_component=(
                    "physical_biology_gate"
                ),
                source_operation=operation
            )
        )

        event = {
            "name": (
                "premature_cat_biology_"
                "replaced_by_cronenberg"
            ),
            "operation": operation,
            "cat": cat_name,
            "physical_universe_started": False,
            "allowed": False,
            "cronenberg_created": True,
            "cronenberg_id": cronenberg.id
        }

        self.history.append(
            event
        )

        self.universe.quantum_events.append(
            event
        )

        return {
            **event,
            "cronenberg": cronenberg
        }