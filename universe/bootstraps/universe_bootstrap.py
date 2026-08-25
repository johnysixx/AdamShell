from universe.layerRegistry import LayerRegistry
from meeting_place.meeting_place import MeetingPlace
from library import Library
from root_universe import RootUniverse
from idea_universe import IdeaUniverse
from core.transitions.root_transition import RootTransition
from cats.cat_distribution_system import CatDistributionSystem


class UniverseBootstrap:

    def __init__(
        self,
        universe_registry,
        universe
    ):
        self.universe_registry = universe_registry
        self.universe = universe

    def run(self):
        self.universe.universe_registry = (
            self.universe_registry
        )

        layers = LayerRegistry()

        # Permanent Multiverse infrastructure exists
        # before quantum physics.
        meeting_place = MeetingPlace(
            self.universe
        )

        layers.register(
            "meeting",
            meeting_place
        )

        layers.register(
            "library",
            Library(self.universe)
        )

        # Idea Universe is pre-physical.
        idea_universe = IdeaUniverse(
            self.universe
        )

        self.universe.meeting_place = (
            meeting_place
        )

        self.universe.idea_universe = (
            idea_universe
        )

        meeting_place.cat_distribution_system = (
            CatDistributionSystem(
                meeting_entities=(
                    meeting_place.entities
                ),
                idea_entities=(
                    idea_universe.entities
                ),
                recipient_registry=(
                    self.universe.cat_recipient_registry
                )
            )
        )

        self.universe.cat_distribution_system = (
            meeting_place.cat_distribution_system
        )

        self.universe.cat_door_registry.create_pair(
            name="front_cat_door",
            layer_a="meeting_place",
            layer_b="meeting_place",
            location_a="outside_front_door",
            location_b="inside_front_door"
        )

        self.universe.cat_door_registry.create_pair(
            name="back_room_cat_door",
            layer_a="meeting_place",
            layer_b="meeting_place",
            location_a="meeting_place",
            location_b="back_room"
        )

        world_cat_door = (
            self.universe
            .cat_door_registry
            .create(
                name="world_cat_door",
                source_layer="meeting_place",
                target_layer=None,
                source_location="back_room",
                destination_mode="cat_choice"
            )
        )

        meeting_place.back_room.attach_world_cat_door(
            world_cat_door
        )


        # Quantum and physical structures are
        # initialized afterwards.
        self.universe.enable_quantum_layer()
        self.universe.boot_physics()

        root_transition = RootTransition()

        layers.register(
            "root_universe",
            RootUniverse(self.universe)
        )

        return (
            root_transition,
            layers,
            idea_universe
        )
