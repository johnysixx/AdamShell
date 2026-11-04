import unittest

from core.eternal_flame.eternal_flame import EternalFlame
from core.eternal_flame.eternal_flame_objects import (
    EternalFlameHistoryRecord,
    EternalFlameSourceIdea,
)
from idea_entities.eternal_fire_potential import EternalFirePotential
from idea_entities.eternal_fire_potential_state import (
    EternalFirePotentialState,
)


class EternalFlameRecordObjectStateTests(unittest.TestCase):

    def _burning_idea(self):
        fire = EternalFirePotential()
        fire.type = "idea_focal_point"
        fire.state = EternalFirePotentialState.BURNING
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

    def test_public_metadata_snapshots_detach_nested_values(self):
        flame = EternalFlame()

        unignited = flame.public_state

        self.assertIsNone(
            unignited["ignited_at_tick"],
        )

        self.assertIsNone(
            unignited["keeper"],
        )

        keeper = {
            "metadata": {
                "roles": ["guardian"],
            },
        }

        tick = {
            "logical": {
                "steps": [1],
            },
        }

        record = flame.ignite(
            self._burning_idea(),
            tick=tick,
            keeper=keeper,
        )

        first = flame.public_state
        second = flame.public_state

        first["keeper"]["metadata"][
            "roles"
        ].append("snapshot_only")

        first["ignited_at_tick"][
            "logical"
        ]["steps"].append(99)

        self.assertEqual(
            keeper["metadata"]["roles"],
            ["guardian"],
        )

        self.assertEqual(
            tick["logical"]["steps"],
            [1],
        )

        self.assertEqual(
            second["keeper"]["metadata"]["roles"],
            ["guardian"],
        )

        self.assertEqual(
            second["ignited_at_tick"][
                "logical"
            ]["steps"],
            [1],
        )

        self.assertEqual(
            first["history"][0]["keeper"][
                "metadata"
            ]["roles"],
            ["guardian"],
        )

        self.assertEqual(
            first["history"][0]["tick"][
                "logical"
            ]["steps"],
            [1],
        )

        self.assertIs(
            flame.keeper,
            keeper,
        )

        self.assertIs(
            flame.ignited_at_tick,
            tick,
        )

        self.assertIs(
            flame.history[0],
            record,
        )

        self.assertIs(
            record.keeper,
            keeper,
        )

        self.assertIs(
            record.tick,
            tick,
        )

    def test_public_metadata_snapshots_ignore_live_changes(self):
        flame = EternalFlame()

        keeper = {
            "metadata": {
                "roles": ["guardian"],
            },
        }

        tick = {
            "logical": {
                "steps": [1],
            },
        }

        record = flame.ignite(
            self._burning_idea(),
            tick=tick,
            keeper=keeper,
        )

        snapshot = flame.public_state

        keeper["metadata"]["roles"].append(
            "live_change"
        )

        tick["logical"]["steps"].append(
            2
        )

        self.assertEqual(
            snapshot["keeper"]["metadata"]["roles"],
            ["guardian"],
        )

        self.assertEqual(
            snapshot["ignited_at_tick"][
                "logical"
            ]["steps"],
            [1],
        )

        self.assertEqual(
            snapshot["history"][0]["keeper"][
                "metadata"
            ]["roles"],
            ["guardian"],
        )

        self.assertEqual(
            snapshot["history"][0]["tick"][
                "logical"
            ]["steps"],
            [1],
        )

        current = flame.public_state

        self.assertEqual(
            current["keeper"]["metadata"]["roles"],
            ["guardian", "live_change"],
        )

        self.assertEqual(
            current["ignited_at_tick"][
                "logical"
            ]["steps"],
            [1, 2],
        )

        self.assertEqual(
            current["history"][0]["keeper"][
                "metadata"
            ]["roles"],
            ["guardian", "live_change"],
        )

        self.assertEqual(
            current["history"][0]["tick"][
                "logical"
            ]["steps"],
            [1, 2],
        )

        self.assertIs(
            flame.keeper,
            keeper,
        )

        self.assertIs(
            flame.ignited_at_tick,
            tick,
        )

        self.assertIs(
            flame.history[0],
            record,
        )

    def test_repeated_ignition_snapshots_keep_history_identity(self):
        flame = EternalFlame()
        idea = self._burning_idea()

        keeper = {
            "roles": ["guardian"],
        }

        initial_tick = {
            "steps": [1],
        }

        retry_tick = {
            "steps": [2],
        }

        first_record = flame.ignite(
            idea,
            tick=initial_tick,
            keeper=keeper,
        )

        history = flame.history

        second_record = flame.ignite(
            idea,
            tick=retry_tick,
        )

        self.assertIs(
            flame.history,
            history,
        )

        self.assertIs(
            flame.history[0],
            first_record,
        )

        self.assertIs(
            flame.history[1],
            second_record,
        )

        self.assertEqual(
            second_record.name,
            "eternal_flame_already_burns",
        )

        self.assertIs(
            second_record.tick,
            retry_tick,
        )

        self.assertIs(
            flame.ignited_at_tick,
            initial_tick,
        )

        self.assertIs(
            flame.keeper,
            keeper,
        )

        first = flame.public_state
        second = flame.public_state

        first["keeper"]["roles"].append(
            "snapshot_only"
        )

        first["ignited_at_tick"]["steps"].append(
            99
        )

        first["history"][1]["tick"][
            "steps"
        ].append(99)

        self.assertEqual(
            keeper["roles"],
            ["guardian"],
        )

        self.assertEqual(
            initial_tick["steps"],
            [1],
        )

        self.assertEqual(
            retry_tick["steps"],
            [2],
        )

        self.assertEqual(
            second["keeper"]["roles"],
            ["guardian"],
        )

        self.assertEqual(
            second["ignited_at_tick"]["steps"],
            [1],
        )

        self.assertEqual(
            second["history"][1]["tick"][
                "steps"
            ],
            [2],
        )

        keeper["roles"].append(
            "live_change"
        )

        initial_tick["steps"].append(
            3
        )

        retry_tick["steps"].append(
            4
        )

        self.assertEqual(
            second["keeper"]["roles"],
            ["guardian"],
        )

        self.assertEqual(
            second["ignited_at_tick"]["steps"],
            [1],
        )

        self.assertEqual(
            second["history"][1]["tick"][
                "steps"
            ],
            [2],
        )

        current = flame.public_state

        self.assertEqual(
            current["keeper"]["roles"],
            ["guardian", "live_change"],
        )

        self.assertEqual(
            current["ignited_at_tick"]["steps"],
            [1, 3],
        )

        self.assertEqual(
            current["history"][1]["tick"][
                "steps"
            ],
            [2, 4],
        )

        self.assertIs(
            flame.history[0],
            first_record,
        )

        self.assertIs(
            flame.history[1],
            second_record,
        )

    def test_repeated_ignition_adds_record_object(self):
        flame = EternalFlame()
        fire = self._burning_idea()

        flame.ignite(fire, tick=1)
        result = flame.ignite(fire, tick=2)

        self.assertEqual(
            result.name,
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
