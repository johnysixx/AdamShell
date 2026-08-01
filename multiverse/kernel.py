from multiverse import UniverseRegistry
from universe.universe import Universe
from universe.bootstraps.entity_bootstrap import EntityBootstrap
from universe.bootstraps.meeting_bootstrap import MeetingBootstrap
from universe.bootstraps.eden_bootstrap import EdenBootstrap
from universe.bootstraps.universe_bootstrap import UniverseBootstrap
from universe.bootstraps.timeline_bootstrap import TimelineBootstrap


class MultiverseKernel:

    def __init__(self):
        self.universe_registry = UniverseRegistry()
        self.universe = Universe()
        self.universe.kernel = self

        self.root_transition = None
        self.layers = None
        self.idea_universe = None

        self.god = None
        self.pazuzu = None
        self.serpent = None
        self.lilith = None
        self.pazuzu_masculine_principle = None

        self.booted = False

    def boot(self):
        if self.booted:
            return self

        self._initialize_multiverse()
        self._initialize_entities()
        self._advance_universe()

        print("`n--- FIRST CRONENBERG TEST ---")
        for test_number in range(1, 6):
            print(f"--- QUANTUM ERROR {test_number} / 5 ---")
            result = self.universe.trigger_test_quantum_error()
            print(result)

            self.universe.tick_universe()
            self.universe.tick_universe()

        print(
            "CRONENBERG COUNT:",
            self.universe.cronenberg_count
        )

        self._prepare_meeting_place()
        self._run_eden()

        self.booted = True
        return self

    def _initialize_multiverse(self):
        (
            self.root_transition,
            self.layers,
            self.idea_universe
        ) = UniverseBootstrap(
            self.universe_registry,
            self.universe
        ).run()

    def _initialize_entities(self):
        (
            self.god,
            self.pazuzu,
            self.serpent,
            self.lilith,
            self.pazuzu_masculine_principle
        ) = EntityBootstrap(
            self.universe,
            self.idea_universe,
            self.root_transition
        ).run()

    def _advance_universe(self):
        TimelineBootstrap(self.universe).run()

    def _prepare_meeting_place(self):
        MeetingBootstrap(
            self.layers,
            self.god,
            self.serpent,
            self.pazuzu
        ).run()

    def _run_eden(self):
        EdenBootstrap(
            self.universe,
            self.layers
        ).run()
