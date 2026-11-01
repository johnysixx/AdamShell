from core.entity.social_entity import SocialEntity
import unittest
from dataclasses import FrozenInstanceError

from core.entity.world_existence_state import (
    WorldExistenceEntry,
    WorldExistenceState,
)
from core.entity.existence import (
    ExistenceRemovalResult,
    ExistenceResolver,
)

class ExistenceResolverTests(unittest.TestCase):

    def test_world_existence_is_immutable_object_state(self):
        state = WorldExistenceState.of(
            idea_universe=20.0,
            root_universe=70.0,
            eden=40.0,
        )

        self.assertEqual(
            state.percent_in("root_universe"),
            70.0,
        )
        self.assertEqual(
            state.percent_in("unknown_world"),
            0.0,
        )
        self.assertEqual(
            state.strongest_world("idea_universe"),
            "root_universe",
        )
        self.assertTrue(state.exists_anywhere())

        updated = state.with_percent(
            "root_universe",
            0.0,
        )

        self.assertIsNot(updated, state)
        self.assertEqual(
            state.percent_in("root_universe"),
            70.0,
        )
        self.assertEqual(
            updated.percent_in("root_universe"),
            0.0,
        )

        with self.assertRaises(TypeError):
            _ = state["root_universe"]

        with self.assertRaises(FrozenInstanceError):
            state.entries = ()

        with self.assertRaises(FrozenInstanceError):
            state.entries[0].percent = 0.0

        for method in ("get", "items", "keys", "values"):
            self.assertFalse(hasattr(state, method))

        snapshot = state.to_dict()
        snapshot["root_universe"] = 0.0
        self.assertEqual(
            state.percent_in("root_universe"),
            70.0,
        )

    def test_mapping_boundary_converts_to_object(self):
        original = {
            "root_universe": 70.0,
            "eden": 40.0,
        }

        entity = SocialEntity.from_mapping({
            "name": "guest",
            "existence_by_world": original,
        })

        self.assertIsInstance(
            entity.existence_by_world,
            WorldExistenceState,
        )

        original["root_universe"] = 0.0

        self.assertEqual(
            entity.existence_by_world.percent_in(
                "root_universe"
            ),
            70.0,
        )

        snapshot = entity.to_dict()
        self.assertIsInstance(
            snapshot["existence_by_world"],
            dict,
        )

        snapshot["existence_by_world"][
            "root_universe"
        ] = 0.0

        self.assertEqual(
            entity.existence_by_world.percent_in(
                "root_universe"
            ),
            70.0,
        )

        with self.assertRaises(TypeError):
            entity.existence_by_world = {}

    def test_native_world_wins_equal_existence(self):
        state = WorldExistenceState.of(
            idea_universe=50.0,
            root_universe=50.0,
            eden=10.0,
        )

        self.assertEqual(
            state.strongest_world("root_universe"),
            "root_universe",
        )

        self.assertEqual(
            state.strongest_world("eden"),
            "idea_universe",
        )

        self.assertEqual(
            WorldExistenceState().strongest_world(
                "gods_layer"
            ),
            "gods_layer",
        )

        with self.assertRaises(ValueError):
            WorldExistenceState(
                entries=(
                    WorldExistenceEntry(
                        "eden", 10.0
                    ),
                    WorldExistenceEntry(
                        "eden", 20.0
                    ),
                )
            )

    def test_remove_from_strongest_world_only(self):
        entity = SocialEntity.from_mapping({'name': 'guest_1', 'native_world': 'idea_universe', 'existence_by_world': {'idea_universe': 20.0, 'root_universe': 70.0, 'eden': 40.0}})
        result = ExistenceResolver.remove_from_strongest_world(entity)
        self.assertIsInstance(result, ExistenceRemovalResult)
        self.assertFalse(hasattr(result, 'get'))
        with self.assertRaises(TypeError):
            _ = result['world']
        self.assertEqual(result.world, 'root_universe')
        self.assertEqual(result.removed_existence_pct, 70.0)
        self.assertEqual(entity.existence_by_world.to_dict(), {'idea_universe': 20.0, 'root_universe': 0.0, 'eden': 40.0})

    def test_entity_still_exists_if_any_world_has_existence(self):
        entity = SocialEntity.from_mapping({'name': 'guest_1', 'native_world': 'idea_universe', 'existence_by_world': {'idea_universe': 20.0, 'root_universe': 70.0, 'eden': 40.0}})
        ExistenceResolver.remove_from_strongest_world(entity)
        self.assertTrue(ExistenceResolver.exists_anywhere(entity))

    def test_entity_no_longer_exists_if_all_worlds_are_zero(self):
        entity = SocialEntity.from_mapping({'name': 'guest_1', 'native_world': 'idea_universe', 'existence_by_world': {'idea_universe': 0.0, 'root_universe': 70.0, 'eden': 0.0}})
        ExistenceResolver.remove_from_strongest_world(entity)
        self.assertFalse(ExistenceResolver.exists_anywhere(entity))

    def test_object_entity_can_remove_strongest_world_existence(self):

        class Guest:
            pass
        entity = Guest()
        entity.name = 'guest_1'
        entity.native_world = 'idea_universe'
        entity.existence_by_world = WorldExistenceState.of(
            idea_universe=20.0,
            root_universe=70.0,
            eden=40.0,
        )
        result = ExistenceResolver.remove_from_strongest_world(entity)
        self.assertEqual(result.world, 'root_universe')
        self.assertEqual(entity.existence_by_world.to_dict(), {'idea_universe': 20.0, 'root_universe': 0.0, 'eden': 40.0})
        self.assertTrue(ExistenceResolver.exists_anywhere(entity))
if __name__ == '__main__':
    unittest.main()
