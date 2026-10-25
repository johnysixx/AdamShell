import unittest

from genesis.day0_first_bar_shift import Day0FirstBarShift
from gods import Gods
from idea_entities import IdeaEntities
from library import Library
from meeting_place.meeting_place import MeetingPlace
from multiverse import UniverseRegistry
from universe.universe import Universe


class Day0HistoryObjectStateTests(unittest.TestCase):

    def test_complete_history_uses_domain_objects(self):
        universe = Universe()
        universe.universe_registry = UniverseRegistry()

        scene = Day0FirstBarShift(
            universe=universe,
            meeting_place=MeetingPlace(universe),
            library=Library(universe),
            gods=Gods(universe),
            idea_entities=IdeaEntities(universe),
        )

        scene.advance_to_bouncer_accepts_judge_role()

        history = scene.history

        self.assertIsInstance(history, list)
        self.assertTrue(history)
        self.assertFalse(hasattr(scene, "_history"))
        self.assertFalse(hasattr(scene, "recorded_events"))

        invalid = [
            (index, type(event).__name__)
            for index, event in enumerate(history)
            if (
                isinstance(event, dict)
                or not isinstance(
                    getattr(event, "name", None), str
                )
                or not callable(
                    getattr(event, "to_dict", None)
                )
            )
        ]

        self.assertEqual(invalid, [])

        checkpoint = scene.checkpoint()
        snapshots = checkpoint["history"]

        self.assertEqual(len(snapshots), len(history))
        self.assertTrue(
            all(isinstance(event, dict) for event in snapshots)
        )
        self.assertEqual(
            [event.name for event in history],
            [event["name"] for event in snapshots],
        )

        original_name = history[0].name
        snapshots[0]["name"] = "modified"

        self.assertEqual(history[0].name, original_name)
        self.assertEqual(
            scene.checkpoint()["history"][0]["name"],
            original_name,
        )


if __name__ == "__main__":
    unittest.main()
