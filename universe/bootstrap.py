from universe.bootstraps.entity_bootstrap import EntityBootstrap
from universe.bootstraps.meeting_bootstrap import MeetingBootstrap
from universe.bootstraps.eden_bootstrap import EdenBootstrap
from universe.bootstraps.universe_bootstrap import UniverseBootstrap
from universe.bootstraps.timeline_bootstrap import TimelineBootstrap


class Bootstrap:

    def _initialize_universe(self):
        (
            self.universe_registry,
            self.universe,
            self.root_transition,
            self.layers,
            self.idea_universe
        ) = UniverseBootstrap().run()

    def _initialize_entities(self):
        entity_bootstrap = EntityBootstrap(
            self.universe,
            self.idea_universe,
            self.root_transition
        )

        (
            self.god,
            self.pazuzu,
            self.serpent,
            self.lilith,
            self.pazuzu_masculine_principle
        ) = entity_bootstrap.run()

    def run(self):
        self._initialize_universe()
        self._initialize_entities()
        self._advance_universe()
        self._prepare_meeting_place()
        self._run_eden()

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






