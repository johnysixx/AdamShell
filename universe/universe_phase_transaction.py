from universe.cronenberg_encounter_batch_transaction import (
    CronenbergEncounterBatchTransaction,
)
from universe.entity_tick_transaction import (
    EntityRuntimeSnapshot,
)


class PhaseObjectSnapshot(EntityRuntimeSnapshot):
    """Capture supported mutable roots of one scheduler phase."""

    def __init__(self, universe, roots):
        self.universe = universe
        self.records = []
        self.seen = set()

        for root in roots:
            self._capture(root, 0)


class UniversePhaseTransaction:
    """Rollback one failed phase before error manifestation."""

    ROOT_NAMES = {
        "layers": (
            "layers",
            "entities",
        ),
        "idea_universe": (
            "idea_universe",
            "entities",
        ),
        "aroma": (
            "quantum_boxes",
            "cats_layer",
        ),
        "spacetime": (
            "spacetime",
            "physics",
        ),
        "physics": (
            "spacetime",
            "physics",
        ),
        "biology": (
            "life_cycle_system",
            "cats_layer",
            "entities",
        ),
        "cats": (
            "cats_layer",
            "entities",
        ),
        "meeting_place": (
            "meeting_place",
            "entities",
        ),
        "statistics": (
            "cronenberg_population_statistics",
            "cats_layer",
        ),
        "history": (
            "life_cycle_system",
        ),
    }

    PROTECTED_PHASES = frozenset(ROOT_NAMES)

    SCALAR_FIELDS = (
        "entropy",
        "pressure",
        "energy_pool",
        "classical_entropy_total",
        "last_classical_entropy_delta",
        "last_energy_gain",
        "last_pressure_cost",
        "last_energy_delta",
        "conflict_pressure",
    )

    @classmethod
    def execute(
        cls,
        universe,
        phase,
        operation,
        target=None,
    ):
        if phase not in cls.PROTECTED_PHASES:
            raise ValueError(
                f"Unsupported phase: {phase!r}"
            )

        scalar_before = tuple(
            (
                name,
                name in universe.__dict__,
                universe.__dict__.get(name),
            )
            for name in cls.SCALAR_FIELDS
        )

        root_states = tuple(
            (
                name,
                name in universe.__dict__,
                universe.__dict__.get(name),
            )
            for name in cls.ROOT_NAMES[phase]
        )

        roots = [
            getattr(universe, name, None)
            for name in cls.ROOT_NAMES[phase]
        ]

        # Optional layers may be passed as external
        # objects, without being stored on Universe.
        if target is not None and target is not universe:
            roots.append(target)

        objects = PhaseObjectSnapshot(
            universe,
            roots,
        )

        try:
            # The existing transaction restores
            # canonical universe registries, quantum
            # state, geometry and RNG on failure.
            return CronenbergEncounterBatchTransaction.execute(
                universe,
                operation,
            )

        except BaseException:
            # Restore phase-specific mutable objects.
            objects.restore()

            # Restore canonical roots if the failed phase
            # rebound an earlier committed object.
            for name, existed, root in root_states:
                if existed:
                    object.__setattr__(
                        universe, name, root
                    )
                else:
                    universe.__dict__.pop(name, None)

            # Restore physical and energetic scalars.
            for name, existed, value in scalar_before:
                if existed:
                    object.__setattr__(
                        universe,
                        name,
                        value,
                    )
                else:
                    universe.__dict__.pop(
                        name,
                        None,
                    )

            # Preserve the original failure, which
            # the scheduler converts to an error
            # result and Cronenberg manifestation.
            raise
