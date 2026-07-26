from universe.universe import Universe
from universe.layerRegistry import LayerRegistry
from meeting_place.meeting_place import MeetingPlace
from library import Library
from root_universe import RootUniverse
from idea_universe import IdeaUniverse
from multiverse import UniverseRegistry
from core.transitions.root_transition import RootTransition


class UniverseBootstrap:

    def run(self):
        universe_registry = UniverseRegistry()

        universe = Universe()
        universe.universe_registry = universe_registry

        universe.enable_quantum_layer()
        universe.boot_physics()

        root_transition = RootTransition()

        layers = LayerRegistry()
        layers.register("meeting", MeetingPlace(universe))
        layers.register("library", Library(universe))

        idea_universe = IdeaUniverse(universe)
        layers.register("root_universe", RootUniverse(universe))

        return (
            universe_registry,
            universe,
            root_transition,
            layers,
            idea_universe
        )
