from universe.layerRegistry import LayerRegistry
from meeting_place.meeting_place import MeetingPlace
from library import Library
from root_universe import RootUniverse
from idea_universe import IdeaUniverse
from core.transitions.root_transition import RootTransition


class UniverseBootstrap:

    def __init__(self, universe_registry, universe):
        self.universe_registry = universe_registry
        self.universe = universe

    def run(self):
        self.universe.universe_registry = self.universe_registry

        layers = LayerRegistry()

        # Permanent Multiverse infrastructure exists before quantum physics.
        layers.register("meeting", MeetingPlace(self.universe))
        layers.register("library", Library(self.universe))

        # Idea Universe is pre-physical.
        idea_universe = IdeaUniverse(self.universe)

        # Quantum and physical structures are initialized afterwards.
        self.universe.enable_quantum_layer()
        self.universe.boot_physics()

        root_transition = RootTransition()
        layers.register("root_universe", RootUniverse(self.universe))

        return (
            root_transition,
            layers,
            idea_universe
        )
