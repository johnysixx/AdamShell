import unittest
from core.entity.social_entity import SocialEntity

from core.entity.serpent_d20 import SerpentD20
from core.eternal_flame.eternal_flame import EternalFlame
from core.eternal_flame.eternal_flame_objects import (
    EternalFlameHistoryRecord,
    EternalFlameSourceIdea,
)
from idea_entities import IdeaEntities
from idea_entities.idea_event_state import IdeaEntityEvent
from idea_entities.eternal_fire_objects import (
    EternalFireFuel,
    EternalFireFuelConsumption,
    EternalFireMeaning,
)
from idea_entities.eternal_fire_potential import (
    EternalFirePotential,
)
from idea_entities.eternal_fire_potential_state import (
    EternalFirePotentialState,
)
from idea_entities.prefysical_fire_origin import (
    PrefysicalFireOrigin,
)
from universe.universe import Universe


class FixedRng:

    def __init__(self, first_roll):
        self.first_roll = first_roll
        self.roll_used = False

    def randint(self, start, end):
        if not self.roll_used:
            self.roll_used = True
            return self.first_roll

        return start

    def random(self):
        return 0.99

    def choice(self, sequence):
        return sequence[0]

    def sample(self, population, k):
        return list(population)[:k]

    def shuffle(self, sequence):
        return None


class MutableSerializedFireInteraction:

    def __init__(self):
        self.metadata = {
            "history": {
                "notes": ["original"],
            },
        }

    def to_dict(self):
        return {
            "name": "test_fire_interaction",
            "metadata": self.metadata,
        }


class EternalFirePotentialObjectStateTests(unittest.TestCase):

    def _system(self):
        universe = Universe()
        idea_entities = IdeaEntities(universe)
        universe.world["pazuzu_masculine_principle"] = SocialEntity(
            name="pazuzu",
            type="idea_entity",
            energy_j=100.0,
        )
        origin = idea_entities.prefysical_fire_origin
        origin.begin()

        return universe, idea_entities, origin

    def test_state_is_object_only(self):
        fire = EternalFirePotential()

        for mapping_method in (
            "get",
            "keys",
            "items",
            "values",
        ):
            self.assertFalse(
                hasattr(fire, mapping_method)
            )

        with self.assertRaises(TypeError):
            _ = fire["state"]

    def test_initial_values_and_public_shape_are_preserved(self):
        fire = EternalFirePotential()

        self.assertEqual(fire.name, "eternal_fire")
        self.assertEqual(fire.type, "idea_fire_potential")
        self.assertIs(
            fire.state,
            EternalFirePotentialState.UNIGNITED,
        )
        self.assertFalse(fire.actualized)
        self.assertIsNone(fire.physical_time)
        self.assertIsNone(fire.physical_location)
        self.assertTrue(fire.requires_maintenance)
        self.assertEqual(
            fire.maintainer,
            "pazuzu_masculine_principle",
        )
        self.assertEqual(fire.interactions, [])
        self.assertEqual(
            set(fire.to_dict()),
            {
                "name",
                "type",
                "state",
                "actualized",
                "physical_time",
                "physical_location",
                "requires_maintenance",
                "maintainer",
                "interactions",
            },
        )

    def test_origin_and_layer_share_same_state_object(self):
        _, idea_entities, origin = self._system()

        self.assertIsInstance(
            idea_entities.eternal_fire,
            EternalFirePotential,
        )
        self.assertIs(
            origin.eternal_fire,
            idea_entities.eternal_fire,
        )

    def test_world_keeps_detached_dict_boundary(self):
        universe, idea_entities, _ = self._system()
        boundary = universe.world["idea_entities"][
            "eternal_fire"
        ]

        self.assertIsInstance(boundary, dict)
        self.assertIsNot(boundary, idea_entities.eternal_fire)

        boundary["state"] = "changed"
        boundary["interactions"].append("changed")

        self.assertIs(
            idea_entities.eternal_fire.state,
            EternalFirePotentialState.UNIGNITED,
        )
        self.assertEqual(
            idea_entities.eternal_fire.interactions,
            [],
        )

    def test_failed_attempt_keeps_same_unactualized_object(self):
        universe, idea_entities, origin = self._system()
        fire = idea_entities.eternal_fire

        result = origin.attempt_ignition(
            rng=FixedRng(10)
        )

        self.assertEqual(result.result, "fire_not_ignited")
        self.assertIs(idea_entities.eternal_fire, fire)
        self.assertFalse(fire.actualized)
        self.assertIs(
            fire.state,
            EternalFirePotentialState.UNIGNITED,
        )
        self.assertFalse(
            universe.world["idea_entities"][
                "eternal_fire"
            ]["actualized"]
        )

    def test_success_mutates_same_object_and_refreshes_boundary(self):
        universe, idea_entities, origin = self._system()
        fire = idea_entities.eternal_fire

        result = origin.attempt_ignition(
            rng=FixedRng(20)
        )
        boundary = universe.world["idea_entities"][
            "eternal_fire"
        ]

        self.assertEqual(
            result.result,
            "prefysical_fire_ignited",
        )
        self.assertIs(idea_entities.eternal_fire, fire)
        self.assertTrue(fire.actualized)
        self.assertIs(
            fire.state,
            EternalFirePotentialState.BURNING,
        )
        self.assertEqual(fire.type, "idea_focal_point")
        self.assertEqual(fire.flame_state, "small")
        self.assertEqual(fire.fuel.wood_sticks, 2.0)
        self.assertTrue(boundary["actualized"])
        self.assertEqual(boundary["state"], "burning")
        self.assertEqual(boundary["fuel"]["wood_sticks"], 2.0)

    def test_significance_mutates_object_and_boundary(self):
        universe, idea_entities, origin = self._system()
        origin.attempt_ignition(rng=FixedRng(20))

        origin.understand_fire_significance()
        fire = idea_entities.eternal_fire
        boundary = universe.world["idea_entities"][
            "eternal_fire"
        ]

        self.assertTrue(fire.meaning.requires_fuel)
        self.assertEqual(
            fire.guardian,
            "pazuzu_masculine_principle",
        )
        self.assertEqual(
            fire.fuel_seekers,
            ["lilith", "serpent"],
        )
        self.assertTrue(boundary["meaning"]["requires_fuel"])
        self.assertEqual(
            boundary["fuel_seekers"],
            ["lilith", "serpent"],
        )

    def test_fuel_advance_mutates_object_and_boundary(self):
        universe, idea_entities, origin = self._system()
        origin.attempt_ignition(rng=FixedRng(20))

        origin.advance_fire()
        fire = idea_entities.eternal_fire
        boundary = universe.world["idea_entities"][
            "eternal_fire"
        ]

        self.assertEqual(fire.fuel.dry_grass, 0.0)
        self.assertEqual(
            fire.fuel_consumed_last_step.dry_grass,
            1.0,
        )
        self.assertEqual(boundary["fuel"]["dry_grass"], 0.0)
        self.assertEqual(
            boundary["fuel_consumed_last_step"]["dry_grass"],
            1.0,
        )

    def test_interaction_mutates_object_and_boundary(self):
        universe, idea_entities, _ = self._system()
        fire = idea_entities.eternal_fire

        interaction = idea_entities.record_fire_interaction(
            name="fire_watched",
            participants=["serpent"],
            observer="lilith",
        )
        boundary = universe.world["idea_entities"][
            "eternal_fire"
        ]

        self.assertIs(idea_entities.eternal_fire, fire)
        self.assertIs(fire.interactions[0], interaction)
        self.assertEqual(
            boundary["interactions"],
            [interaction.to_dict()],
        )

    def test_fire_interaction_preserves_event_identity(
        self
    ):
        universe, layer, _ = self._system()

        event = layer.record_fire_interaction(
            name="fire_observed",
            participants=["serpent", "lilith"],
            observer=None,
        )

        self.assertIsInstance(
            event,
            IdeaEntityEvent,
        )
        self.assertEqual(event.place, "eternal_fire")
        self.assertEqual(event.known_by, ())

        self.assertIs(
            layer.eternal_fire.interactions[-1],
            event,
        )
        self.assertIs(layer.events[-1], event)
        self.assertIs(layer.event_history[-1], event)

        snapshot = universe.world[
            "idea_entities"
        ]["eternal_fire"]["interactions"][-1]

        self.assertEqual(
            snapshot,
            event.to_dict(),
        )

        snapshot["participants"][0] = "changed"

        self.assertEqual(
            event.participants,
            ("serpent", "lilith"),
        )

    def test_nested_guardian_snapshot_is_detached(self):
        guardian = {
            "name": "pazuzu",
            "permissions": {
                "roles": ["guardian"],
            },
        }

        fire = EternalFirePotential()
        fire.guardian = guardian

        first = fire.to_dict()
        second = fire.to_dict()

        first["guardian"]["permissions"][
            "roles"
        ].append("snapshot_only")

        self.assertEqual(
            guardian["permissions"]["roles"],
            ["guardian"],
        )

        self.assertEqual(
            second["guardian"]["permissions"][
                "roles"
            ],
            ["guardian"],
        )

        self.assertIs(
            fire.guardian,
            guardian,
        )

        self.assertIsNot(
            first["guardian"],
            guardian,
        )

        guardian["permissions"][
            "roles"
        ].append("live_change")

        self.assertEqual(
            second["guardian"]["permissions"][
                "roles"
            ],
            ["guardian"],
        )

        self.assertEqual(
            fire.to_dict()["guardian"][
                "permissions"
            ]["roles"],
            ["guardian", "live_change"],
        )

    def test_nested_fuel_seekers_snapshots_are_detached(self):
        seeker = {
            "name": "serpent",
            "metadata": {
                "notes": ["original"],
            },
        }

        fire = EternalFirePotential()
        fire.fuel_seekers.append(seeker)

        first = fire.to_dict()
        second = fire.to_dict()

        first["fuel_seekers"][0]["metadata"][
            "notes"
        ].append("snapshot_only")

        self.assertEqual(
            seeker["metadata"]["notes"],
            ["original"],
        )

        self.assertEqual(
            second["fuel_seekers"][0][
                "metadata"
            ]["notes"],
            ["original"],
        )

        self.assertIs(
            fire.fuel_seekers[0],
            seeker,
        )

        self.assertIsNot(
            first["fuel_seekers"][0],
            seeker,
        )

        seeker["metadata"][
            "notes"
        ].append("live_change")

        self.assertEqual(
            second["fuel_seekers"][0][
                "metadata"
            ]["notes"],
            ["original"],
        )

        self.assertEqual(
            fire.to_dict()["fuel_seekers"][0][
                "metadata"
            ]["notes"],
            ["original", "live_change"],
        )

    def test_world_fire_snapshots_preserve_live_role_identity(self):
        universe = Universe()
        layer = IdeaEntities(universe)

        fire = layer.eternal_fire

        guardian = {
            "name": "pazuzu",
            "notes": ["original"],
        }

        seeker = {
            "name": "lilith",
            "notes": ["original"],
        }

        fire.guardian = guardian
        fire.fuel_seekers.append(seeker)

        layer.write_to_world()

        world_snapshot = universe.world[
            "idea_entities"
        ]["eternal_fire"]

        state_snapshot = universe.world[
            "idea_entities"
        ]["idea_entities_state"]["eternal_fire"]

        public_snapshot = layer.public_state[
            "eternal_fire"
        ]

        self.assertIs(
            layer.eternal_fire,
            fire,
        )

        self.assertIs(
            layer.idea_entities_state.eternal_fire,
            fire,
        )

        self.assertIs(
            fire.guardian,
            guardian,
        )

        self.assertIs(
            fire.fuel_seekers[0],
            seeker,
        )

        world_snapshot["guardian"][
            "notes"
        ].append("snapshot_only")

        world_snapshot["fuel_seekers"][0][
            "notes"
        ].append("snapshot_only")

        self.assertEqual(
            guardian["notes"],
            ["original"],
        )

        self.assertEqual(
            seeker["notes"],
            ["original"],
        )

        for snapshot in (
            state_snapshot,
            public_snapshot,
        ):
            self.assertEqual(
                snapshot["guardian"]["notes"],
                ["original"],
            )

            self.assertEqual(
                snapshot["fuel_seekers"][0][
                    "notes"
                ],
                ["original"],
            )

        guardian["notes"].append(
            "live_change"
        )

        seeker["notes"].append(
            "live_change"
        )

        self.assertEqual(
            state_snapshot["guardian"][
                "notes"
            ],
            ["original"],
        )

        self.assertEqual(
            public_snapshot["fuel_seekers"][0][
                "notes"
            ],
            ["original"],
        )

        current = layer.public_state[
            "eternal_fire"
        ]

        self.assertEqual(
            current["guardian"]["notes"],
            ["original", "live_change"],
        )

        self.assertEqual(
            current["fuel_seekers"][0][
                "notes"
            ],
            ["original", "live_change"],
        )

        self.assertIs(
            layer.eternal_fire,
            fire,
        )

    def test_physical_snapshots_detach_nested_data(self):
        clock = {
            "phase": {
                "ticks": [1],
            },
        }

        location = {
            "coordinates": {
                "x": [2.0],
            },
        }

        fire = EternalFirePotential()
        fire.physical_time = clock
        fire.physical_location = location

        first = fire.to_dict()
        second = fire.to_dict()

        first["physical_time"]["phase"][
            "ticks"
        ].append(999)

        first["physical_location"][
            "coordinates"
        ]["x"].append(999.0)

        self.assertEqual(
            clock["phase"]["ticks"],
            [1],
        )

        self.assertEqual(
            location["coordinates"]["x"],
            [2.0],
        )

        self.assertEqual(
            second["physical_time"]["phase"][
                "ticks"
            ],
            [1],
        )

        self.assertEqual(
            second["physical_location"][
                "coordinates"
            ]["x"],
            [2.0],
        )

        self.assertIs(
            fire.physical_time,
            clock,
        )

        self.assertIs(
            fire.physical_location,
            location,
        )

        self.assertIsNot(
            first["physical_time"],
            clock,
        )

        self.assertIsNot(
            first["physical_location"],
            location,
        )

    def test_physical_snapshots_ignore_later_live_changes(self):
        fire = EternalFirePotential()

        clock = {
            "history": ["original"],
        }

        location = {
            "route": ["origin"],
        }

        fire.physical_time = clock
        fire.physical_location = location

        snapshot = fire.to_dict()

        clock["history"].append("live_change")
        location["route"].append("live_change")

        self.assertEqual(
            snapshot["physical_time"][
                "history"
            ],
            ["original"],
        )

        self.assertEqual(
            snapshot["physical_location"][
                "route"
            ],
            ["origin"],
        )

        current = fire.to_dict()

        self.assertEqual(
            current["physical_time"][
                "history"
            ],
            ["original", "live_change"],
        )

        self.assertEqual(
            current["physical_location"][
                "route"
            ],
            ["origin", "live_change"],
        )

        self.assertIs(
            fire.physical_time,
            clock,
        )

        self.assertIs(
            fire.physical_location,
            location,
        )

    def test_world_physical_snapshots_keep_live_fire_identity(self):
        universe = Universe()
        layer = IdeaEntities(universe)

        fire = layer.eternal_fire

        clock = {
            "history": ["original"],
        }

        location = {
            "coordinates": {
                "x": [2.0],
            },
        }

        fire.physical_time = clock
        fire.physical_location = location

        layer.write_to_world()

        boundary = universe.world[
            "idea_entities"
        ]

        world_snapshot = boundary[
            "eternal_fire"
        ]

        state_snapshot = boundary[
            "idea_entities_state"
        ]["eternal_fire"]

        public_snapshot = layer.public_state[
            "eternal_fire"
        ]

        self.assertIs(
            layer.eternal_fire,
            fire,
        )

        self.assertIs(
            layer.idea_entities_state.eternal_fire,
            fire,
        )

        self.assertIs(
            universe.world["idea_entities_state"],
            layer.idea_entities_state,
        )

        self.assertIs(
            fire.physical_time,
            clock,
        )

        self.assertIs(
            fire.physical_location,
            location,
        )

        world_snapshot["physical_time"][
            "history"
        ].append("snapshot_only")

        world_snapshot["physical_location"][
            "coordinates"
        ]["x"].append(999.0)

        self.assertEqual(
            clock["history"],
            ["original"],
        )

        self.assertEqual(
            location["coordinates"]["x"],
            [2.0],
        )

        for snapshot in (
            state_snapshot,
            public_snapshot,
        ):
            self.assertEqual(
                snapshot["physical_time"][
                    "history"
                ],
                ["original"],
            )

            self.assertEqual(
                snapshot["physical_location"][
                    "coordinates"
                ]["x"],
                [2.0],
            )

        clock["history"].append(
            "live_change"
        )

        location["coordinates"][
            "x"
        ].append(3.0)

        self.assertEqual(
            state_snapshot["physical_time"][
                "history"
            ],
            ["original"],
        )

        self.assertEqual(
            public_snapshot["physical_location"][
                "coordinates"
            ]["x"],
            [2.0],
        )

        current = layer.public_state[
            "eternal_fire"
        ]

        self.assertEqual(
            current["physical_time"][
                "history"
            ],
            ["original", "live_change"],
        )

        self.assertEqual(
            current["physical_location"][
                "coordinates"
            ]["x"],
            [2.0, 3.0],
        )

        self.assertIs(
            layer.eternal_fire,
            fire,
        )

    def test_ignition_metadata_snapshots_are_detached(self):
        fields = (
            "ignited_by",
            "ignited_at_idea_tick",
            "ignited_at_logical_step",
            "flame_state",
            "origin_roll_id",
        )

        fire = EternalFirePotential(
            actualized=True,
        )

        sources = {}

        for name in fields:
            source = {
                "history": ["original"],
            }

            sources[name] = source
            setattr(fire, name, source)

        first = fire.to_dict()
        second = fire.to_dict()

        for name in fields:
            first[name]["history"].append(
                "snapshot_only"
            )

            self.assertEqual(
                sources[name]["history"],
                ["original"],
            )

            self.assertEqual(
                second[name]["history"],
                ["original"],
            )

            self.assertEqual(
                fire.to_dict()[name]["history"],
                ["original"],
            )

            self.assertIs(
                getattr(fire, name),
                sources[name],
            )

            self.assertIsNot(
                first[name],
                sources[name],
            )

    def test_ignition_snapshots_ignore_later_changes(self):
        fields = (
            "ignited_by",
            "ignited_at_idea_tick",
            "ignited_at_logical_step",
            "flame_state",
            "origin_roll_id",
        )

        fire = EternalFirePotential(
            actualized=True,
        )

        sources = {
            name: {"values": ["original"]}
            for name in fields
        }

        for name, source in sources.items():
            setattr(fire, name, source)

        snapshot = fire.to_dict()

        for source in sources.values():
            source["values"].append(
                "live_change"
            )

        current = fire.to_dict()

        for name in fields:
            self.assertEqual(
                snapshot[name]["values"],
                ["original"],
            )

            self.assertEqual(
                current[name]["values"],
                ["original", "live_change"],
            )

            self.assertIs(
                getattr(fire, name),
                sources[name],
            )

        unignited = EternalFirePotential()
        unignited_snapshot = unignited.to_dict()

        for name in fields:
            self.assertNotIn(
                name,
                unignited_snapshot,
            )

    def test_world_ignition_snapshots_keep_fire_identity(self):
        universe = Universe()
        layer = IdeaEntities(universe)

        fire = layer.eternal_fire

        fields = (
            "ignited_by",
            "ignited_at_idea_tick",
            "ignited_at_logical_step",
            "flame_state",
            "origin_roll_id",
        )

        sources = {
            name: {"history": ["original"]}
            for name in fields
        }

        fire.state = EternalFirePotentialState.BURNING
        fire.actualized = True

        for name, source in sources.items():
            setattr(fire, name, source)

        layer.write_to_world()

        boundary = universe.world[
            "idea_entities"
        ]

        world_snapshot = boundary[
            "eternal_fire"
        ]

        state_snapshot = boundary[
            "idea_entities_state"
        ]["eternal_fire"]

        public_snapshot = layer.public_state[
            "eternal_fire"
        ]

        self.assertIs(
            layer.eternal_fire,
            fire,
        )

        self.assertIs(
            layer.idea_entities_state.eternal_fire,
            fire,
        )

        self.assertIs(
            universe.world["idea_entities_state"],
            layer.idea_entities_state,
        )

        for name in fields:
            self.assertIs(
                getattr(fire, name),
                sources[name],
            )

            world_snapshot[name]["history"].append(
                "snapshot_only"
            )

            self.assertEqual(
                sources[name]["history"],
                ["original"],
            )

            self.assertEqual(
                state_snapshot[name]["history"],
                ["original"],
            )

            self.assertEqual(
                public_snapshot[name]["history"],
                ["original"],
            )

        for source in sources.values():
            source["history"].append(
                "live_change"
            )

        current = layer.public_state[
            "eternal_fire"
        ]

        for name in fields:
            self.assertEqual(
                state_snapshot[name]["history"],
                ["original"],
            )

            self.assertEqual(
                public_snapshot[name]["history"],
                ["original"],
            )

            self.assertEqual(
                current[name]["history"],
                ["original", "live_change"],
            )

        self.assertIs(
            layer.eternal_fire,
            fire,
        )

    def test_nested_interaction_snapshot_is_detached(self):
        interaction = MutableSerializedFireInteraction()

        fire = EternalFirePotential()
        fire.interactions.append(interaction)

        first = fire.to_dict()
        second = fire.to_dict()

        first["interactions"][0]["metadata"][
            "history"
        ]["notes"].append("snapshot_only")

        self.assertEqual(
            interaction.metadata["history"]["notes"],
            ["original"],
        )

        self.assertEqual(
            second["interactions"][0]["metadata"][
                "history"
            ]["notes"],
            ["original"],
        )

        self.assertEqual(
            fire.to_dict()["interactions"][0][
                "metadata"
            ]["history"]["notes"],
            ["original"],
        )

        self.assertIs(
            fire.interactions[0],
            interaction,
        )

        self.assertIsNot(
            first["interactions"][0]["metadata"],
            interaction.metadata,
        )

    def test_interaction_snapshot_ignores_live_changes(self):
        interaction = MutableSerializedFireInteraction()

        fire = EternalFirePotential()
        fire.interactions.append(interaction)

        snapshot = fire.to_dict()

        interaction.metadata["history"][
            "notes"
        ].append("live_change")

        self.assertEqual(
            snapshot["interactions"][0]["metadata"][
                "history"
            ]["notes"],
            ["original"],
        )

        current = fire.to_dict()

        self.assertEqual(
            current["interactions"][0]["metadata"][
                "history"
            ]["notes"],
            ["original", "live_change"],
        )

        snapshot["interactions"].clear()

        self.assertEqual(
            len(fire.interactions),
            1,
        )

        self.assertIs(
            fire.interactions[0],
            interaction,
        )

    def test_world_interaction_snapshots_keep_event_identity(self):
        universe = Universe()
        layer = IdeaEntities(universe)

        canonical = layer.record_fire_interaction(
            name="fire_observed",
            participants=["serpent"],
            observer="lilith",
        )

        fire = layer.eternal_fire

        interaction = MutableSerializedFireInteraction()
        fire.interactions.append(interaction)

        layer.write_to_world()

        boundary = universe.world[
            "idea_entities"
        ]

        world_snapshot = boundary[
            "eternal_fire"
        ]

        state_snapshot = boundary[
            "idea_entities_state"
        ]["eternal_fire"]

        public_snapshot = layer.public_state[
            "eternal_fire"
        ]

        self.assertIs(
            layer.eternal_fire,
            fire,
        )

        self.assertIs(
            layer.idea_entities_state.eternal_fire,
            fire,
        )

        self.assertIs(
            fire.interactions[0],
            canonical,
        )

        self.assertIs(
            layer.events[-1],
            canonical,
        )

        self.assertIs(
            layer.event_history[-1],
            canonical,
        )

        self.assertIs(
            fire.interactions[1],
            interaction,
        )

        self.assertEqual(
            world_snapshot["interactions"][0],
            canonical.to_dict(),
        )

        world_snapshot["interactions"][1][
            "metadata"
        ]["history"]["notes"].append("snapshot_only")

        self.assertEqual(
            interaction.metadata["history"]["notes"],
            ["original"],
        )

        for snapshot in (
            state_snapshot,
            public_snapshot,
        ):
            self.assertEqual(
                snapshot["interactions"][1][
                    "metadata"
                ]["history"]["notes"],
                ["original"],
            )

        interaction.metadata["history"][
            "notes"
        ].append("live_change")

        self.assertEqual(
            state_snapshot["interactions"][1][
                "metadata"
            ]["history"]["notes"],
            ["original"],
        )

        self.assertEqual(
            public_snapshot["interactions"][1][
                "metadata"
            ]["history"]["notes"],
            ["original"],
        )

        current = layer.public_state[
            "eternal_fire"
        ]

        self.assertEqual(
            current["interactions"][1][
                "metadata"
            ]["history"]["notes"],
            ["original", "live_change"],
        )

        self.assertIs(
            fire.interactions[0],
            canonical,
        )

        self.assertIs(
            fire.interactions[1],
            interaction,
        )

    def test_to_dict_is_deeply_detached(self):
        fire = EternalFirePotential()
        fire.actualized = True
        fire.set_fuel(
            EternalFireFuel(wood_sticks=2.0)
        )
        fire.set_meaning(
            EternalFireMeaning()
        )
        fire.interactions.append(
            IdeaEntityEvent(
                name="watched",
                participants=(),
            )
        )

        snapshot = fire.to_dict()
        snapshot["fuel"]["wood_sticks"] = 999.0
        snapshot["meaning"]["requires_fuel"] = False
        snapshot["interactions"][0]["name"] = "changed"

        self.assertEqual(fire.fuel.wood_sticks, 2.0)
        self.assertTrue(fire.meaning.requires_fuel)
        self.assertEqual(
            fire.interactions[0].name,
            "watched",
        )

    def test_fire_substate_is_object_only(self):
        universe, idea_entities, origin = self._system()
        origin.attempt_ignition(rng=FixedRng(20))
        origin.understand_fire_significance()
        origin.advance_fire()

        fire = idea_entities.eternal_fire

        self.assertIsInstance(fire.fuel, EternalFireFuel)
        self.assertIsInstance(fire.meaning, EternalFireMeaning)
        self.assertIsInstance(
            fire.fuel_consumed_last_step,
            EternalFireFuelConsumption,
        )

        for value in (
            fire.fuel,
            fire.meaning,
            fire.fuel_consumed_last_step,
        ):
            self.assertFalse(hasattr(value, "get"))
            self.assertFalse(hasattr(value, "items"))

        with self.assertRaises(TypeError):
            _ = fire.fuel["dry_grass"]
        with self.assertRaises(TypeError):
            _ = fire.meaning["requires_fuel"]
        with self.assertRaises(TypeError):
            _ = fire.fuel_consumed_last_step["dry_grass"]

    def test_fire_rejects_legacy_substate_dicts(self):
        fire = EternalFirePotential()

        with self.assertRaises(TypeError):
            fire.set_fuel({"wood_sticks": 2.0})

        with self.assertRaises(TypeError):
            fire.set_meaning({"requires_fuel": True})

        with self.assertRaises(TypeError):
            fire.record_fuel_consumption({"dry_grass": 1.0})

    def test_string_state_is_rejected(self):
        fire = EternalFirePotential()

        with self.assertRaises(TypeError):
            fire.state = "burning"

    def test_state_values_define_domain_names(self):
        self.assertEqual(
            {
                state.value
                for state in EternalFirePotentialState
            },
            {
                "unignited",
                "burning",
            },
        )

    def test_origin_rejects_old_mapping_state(self):
        with self.assertRaises(TypeError):
            PrefysicalFireOrigin(
                eternal_fire={"name": "eternal_fire"},
                serpent_d20=SerpentD20(),
            )

    def test_eternal_flame_accepts_object_and_rejects_mapping(self):
        fire = EternalFirePotential()
        fire.type = "idea_focal_point"
        fire.state = EternalFirePotentialState.BURNING
        fire.actualized = True
        flame = EternalFlame()

        result = flame.ignite(
            fire,
            tick=1,
            keeper="pazuzu",
        )

        self.assertEqual(result.name, "eternal_flame_ignited")
        self.assertEqual(result.source_idea.name, "eternal_fire")
        self.assertEqual(result.source_idea.type, "idea_focal_point")
        self.assertEqual(result.source_idea.state, "burning")
        self.assertIsInstance(
            flame.source_idea,
            EternalFlameSourceIdea,
        )
        self.assertIsInstance(
            flame.history[0],
            EternalFlameHistoryRecord,
        )
        self.assertFalse(hasattr(flame.source_idea, "get"))
        self.assertFalse(hasattr(flame.history[0], "get"))

        with self.assertRaises(TypeError):
            _ = flame.source_idea["name"]

        with self.assertRaises(TypeError):
            _ = flame.history[0]["name"]

        boundary = flame.public_state
        boundary["source_idea"]["state"] = "changed"
        boundary["history"][0]["source_idea"]["state"] = "changed"

        self.assertEqual(flame.source_idea.state, "burning")
        self.assertEqual(
            flame.history[0].source_idea.state,
            "burning",
        )

        second = flame.ignite(
            fire,
            tick=2,
            keeper="pazuzu",
        )
        self.assertEqual(
            second.name,
            "eternal_flame_already_burns",
        )
        self.assertIsInstance(
            flame.history[1],
            EternalFlameHistoryRecord,
        )

        with self.assertRaises(TypeError):
            EternalFlame().ignite(fire.to_dict())


if __name__ == "__main__":
    unittest.main()
