import unittest
from types import SimpleNamespace

from core.entity.entity import Entity
from meeting_place.bar_entity_policy import BarEntityPolicy
from meeting_place.glass_shelf import GlassShelf
from universe.universe import Universe


class UniverseWorldEntityRegistrationObjectStateTests(
    unittest.TestCase
):

    def _universe_with_bar(self):
        universe = Universe()

        place = SimpleNamespace(
            glass_shelf=GlassShelf(),
            bar_entity_policy=BarEntityPolicy(),
        )

        universe.meeting_place = place

        return universe, place

    @staticmethod
    def _count_glasses(place, kind):
        return sum(
            glass.kind == kind
            for glass in place.glass_shelf.shared_glasses
        )

    def test_typed_cat_ignores_conflicting_world_record(
        self
    ):
        universe, place = self._universe_with_bar()

        universe.world["typed_cat"] = {
            "type": "cronenberg",
        }

        cat = SimpleNamespace(
            name="typed_cat",
            type="cat",
            profile={
                "name": "typed_cat",
                "type": "cat",
            },
        )

        universe.add_entity(cat)

        self.assertIs(
            cat.universe,
            universe,
        )
        self.assertIn(
            cat,
            universe.entities,
        )

        self.assertEqual(
            self._count_glasses(place, "beer_mug"),
            1,
        )
        self.assertEqual(
            self._count_glasses(place, "shot_glass"),
            0,
        )

        self.assertEqual(
            cat.bar_policy.service_mode,
            "cat",
        )

    def test_typed_cronenberg_ignores_world_record(
        self
    ):
        universe, place = self._universe_with_bar()

        universe.world["typed_cronenberg"] = {
            "type": "cat",
        }

        entity = SimpleNamespace(
            name="typed_cronenberg",
            type="cronenberg",
            profile=None,
        )

        universe.add_entity(entity)

        self.assertEqual(
            self._count_glasses(place, "shot_glass"),
            1,
        )
        self.assertEqual(
            self._count_glasses(place, "beer_mug"),
            0,
        )

        self.assertIsNotNone(
            entity.bar_policy,
        )

    def test_untyped_entity_does_not_infer_world_type(
        self
    ):
        universe, place = self._universe_with_bar()

        universe.world["untyped_entity"] = {
            "type": "cat",
        }

        entity = SimpleNamespace(
            name="untyped_entity",
            profile=None,
        )

        universe.add_entity(entity)

        self.assertEqual(
            self._count_glasses(place, "beer_mug"),
            0,
        )
        self.assertEqual(
            self._count_glasses(place, "shot_glass"),
            0,
        )

        self.assertEqual(
            entity.bar_policy.entity_class,
            "unclassified",
        )

        self.assertIn(
            entity,
            universe.entities,
        )

    def test_legacy_profile_still_drives_bar_policy(
        self
    ):
        universe, place = self._universe_with_bar()

        entity = SimpleNamespace(
            name="profiled_cat",
            profile={
                "name": "profiled_cat",
                "type": "cat",
            },
        )

        universe.add_entity(entity)

        self.assertFalse(
            hasattr(entity, "type")
        )

        self.assertEqual(
            self._count_glasses(place, "beer_mug"),
            0,
        )

        self.assertEqual(
            entity.bar_policy.service_mode,
            "cat",
        )
        self.assertEqual(
            entity.bar_policy.glass_mode,
            "none",
        )

    def test_add_entity_does_not_read_world_mapping(
        self
    ):
        class WorldWithoutGet(dict):

            def get(self, key, default=None):
                raise AssertionError(
                    "add_entity must not read world.get"
                )

        universe, place = self._universe_with_bar()

        universe.world = WorldWithoutGet(
            universe.world
        )

        entity = SimpleNamespace(
            name="canonical_cat",
            type="cat",
            profile={
                "name": "canonical_cat",
                "type": "cat",
            },
        )

        universe.add_entity(entity)

        self.assertIs(
            entity.universe,
            universe,
        )
        self.assertIn(
            entity,
            universe.entities,
        )

        self.assertEqual(
            self._count_glasses(place, "beer_mug"),
            1,
        )

    def test_create_entity_retains_profile_resolution(
        self
    ):
        universe, place = self._universe_with_bar()

        profile = {
            "entity_id": "profiled_generic",
            "name": "profiled_generic",
            "type": "cat",
        }

        universe.world[
            "profiled_generic"
        ] = profile

        entity = universe.create_entity(
            "profiled_generic"
        )

        self.assertIsInstance(
            entity,
            Entity,
        )

        self.assertIs(
            entity.profile,
            profile,
        )

        self.assertFalse(
            hasattr(entity, "type")
        )

        self.assertEqual(
            self._count_glasses(place, "beer_mug"),
            0,
        )

        self.assertEqual(
            entity.bar_policy.service_mode,
            "cat",
        )

        self.assertIn(
            entity,
            universe.entities,
        )


if __name__ == "__main__":
    unittest.main()
