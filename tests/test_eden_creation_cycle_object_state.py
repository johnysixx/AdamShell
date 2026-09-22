import unittest

from eden import Eden
from eden.creation_objects import (
    CreationDarkness,
    CreationDayPhase,
    CreationDayRecord,
    CreationLight,
)
from universe.physics_state import UniverseTimeState
from universe.universe import Universe


class EdenCreationCycleObjectStateTests(unittest.TestCase):

    def _created_day_zero(self):
        universe = Universe()
        eden = Eden(universe)
        eden.day_0()

        return universe, eden

    def _assert_object_only(self, value, key):
        for mapping_method in (
            "get",
            "keys",
            "items",
            "values",
        ):
            self.assertFalse(
                hasattr(value, mapping_method)
            )

        with self.assertRaises(TypeError):
            _ = value[key]

    def test_day_zero_creates_object_state(self):
        universe, _ = self._created_day_zero()

        self.assertIsInstance(
            universe.world["light"],
            CreationLight,
        )
        self.assertIsInstance(
            universe.physics["darkness"],
            CreationDarkness,
        )
        self.assertIsInstance(
            universe.world["evening"],
            CreationDayPhase,
        )
        self.assertIsInstance(
            universe.world["morning"],
            CreationDayPhase,
        )
        self.assertIsInstance(
            universe.world["creation_day"],
            CreationDayRecord,
        )

    def test_light_preserves_creation_state(self):
        universe, _ = self._created_day_zero()
        light = universe.world["light"]

        self.assertEqual(light.intensity, 1.0)
        self.assertEqual(light.state, "primordial")
        self.assertEqual(light.speed, 299792458)
        self.assertTrue(light.constant)
        self.assertEqual(light.name, "day")
        self.assertTrue(light.good)
        self._assert_object_only(
            light,
            "state",
        )

    def test_darkness_and_day_phases_preserve_state(self):
        universe, _ = self._created_day_zero()

        darkness = universe.physics["darkness"]
        evening = universe.world["evening"]
        morning = universe.world["morning"]
        creation_day = universe.world[
            "creation_day"
        ]

        self.assertEqual(
            darkness.name,
            "night",
        )
        self.assertEqual(
            darkness.state,
            "primordial",
        )
        self.assertEqual(
            (evening.day, evening.state),
            (0, "evening"),
        )
        self.assertEqual(
            (morning.day, morning.state),
            (0, "morning"),
        )
        self.assertEqual(
            creation_day.day,
            0,
        )
        self.assertEqual(
            creation_day.name,
            "first day of the creation",
        )
        self.assertTrue(
            creation_day.complete
        )

        self._assert_object_only(
            darkness,
            "state",
        )
        self._assert_object_only(
            evening,
            "state",
        )
        self._assert_object_only(
            morning,
            "state",
        )
        self._assert_object_only(
            creation_day,
            "complete",
        )

    def test_eden_reuses_universe_time_state(self):
        universe, _ = self._created_day_zero()

        time_state = universe.physics["time"]

        self.assertIsInstance(
            time_state,
            UniverseTimeState,
        )
        self.assertIs(
            universe.world["time"],
            time_state,
        )

    def test_light_changes_through_domain_methods(self):
        light = CreationLight()

        self.assertIsNone(light.name)
        self.assertFalse(light.good)

        light.name_as_day()
        light.mark_good()

        self.assertEqual(
            light.name,
            "day",
        )
        self.assertTrue(light.good)

    def test_snapshots_are_detached_dict_boundaries(self):
        universe, _ = self._created_day_zero()

        light = universe.world["light"]
        darkness = universe.physics["darkness"]
        evening = universe.world["evening"]
        creation_day = universe.world[
            "creation_day"
        ]

        light_snapshot = light.to_dict()
        darkness_snapshot = darkness.to_dict()
        evening_snapshot = evening.to_dict()
        day_snapshot = creation_day.to_dict()

        light_snapshot["name"] = "changed"
        darkness_snapshot["name"] = "changed"
        evening_snapshot["state"] = "changed"
        day_snapshot["complete"] = False

        self.assertEqual(
            light.name,
            "day",
        )
        self.assertEqual(
            darkness.name,
            "night",
        )
        self.assertEqual(
            evening.state,
            "evening",
        )
        self.assertTrue(
            creation_day.complete
        )


if __name__ == "__main__":
    unittest.main()
