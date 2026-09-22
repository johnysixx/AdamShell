import unittest

from core.eternal_flame.eternal_flame import EternalFlame
from core.eternal_flame.eternal_flame_objects import (
    EternalFlameHistoryRecord,
    EternalFlameSourceIdea,
)
from idea_entities.eternal_fire_potential import EternalFirePotential


class EternalFlameRecordObjectStateTests(unittest.TestCase):

    def _burning_idea(self):
        fire = EternalFirePotential()
        fire.type = "idea_focal_point"
        fire.state = "burning"
        fire.actualized = True
        return fire

    def test_ignition_stores_source_and_history_objects(self):
        flame = EternalFlame()
        flame.ignite(
            self._burning_idea(),
            tick=1,
            keeper="pazuzu",
        )

        self.assertIsInstance(
            flame.source_idea,
            EternalFlameSourceIdea,
        )
        self.assertIsInstance(
            flame.history[0],
            EternalFlameHistoryRecord,
        )
        self.assertIs(
            flame.history[0].source_idea,
            flame.source_idea,
        )

    def test_live_flame_records_are_object_only(self):
        flame = EternalFlame()
        flame.ignite(self._burning_idea())

        for value in (
            flame.source_idea,
            flame.history[0],
        ):
            self.assertFalse(hasattr(value, "get"))
            self.assertFalse(hasattr(value, "items"))

        with self.assertRaises(TypeError):
            _ = flame.source_idea["name"]

        with self.assertRaises(TypeError):
            _ = flame.history[0]["name"]

    def test_public_state_serializes_detached_records(self):
        flame = EternalFlame()
        flame.ignite(
            self._burning_idea(),
            tick=1,
            keeper="pazuzu",
        )

        public_state = flame.public_state
        public_state["source_idea"]["state"] = "changed"
        public_state["history"][0]["source_idea"]["state"] = "changed"

        self.assertEqual(
            flame.source_idea.state,
            "burning",
        )
        self.assertEqual(
            flame.history[0].source_idea.state,
            "burning",
        )

    def test_repeated_ignition_adds_record_object(self):
        flame = EternalFlame()
        fire = self._burning_idea()

        flame.ignite(fire, tick=1)
        result = flame.ignite(fire, tick=2)

        self.assertEqual(
            result["name"],
            "eternal_flame_already_burns",
        )
        self.assertIsInstance(
            flame.history[1],
            EternalFlameHistoryRecord,
        )
        self.assertEqual(
            flame.history[1].state,
            "burning",
        )
        self.assertEqual(
            flame.history[1].tick,
            2,
        )


if __name__ == "__main__":
    unittest.main()
