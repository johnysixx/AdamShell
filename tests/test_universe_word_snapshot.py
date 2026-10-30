import unittest

from core.word.word import Word
from core.word.chronicle import Chronicle
from universe.universe import Universe


class UniverseWordSnapshotTests(unittest.TestCase):

    def make_chronicle(self, *names):
        chronicle = Chronicle()

        for name in names:
            chronicle.record(Word(name))

        return chronicle

    def test_snapshot_contains_replayed_word_state(self):
        chronicle = self.make_chronicle(
            "LetThereBeLight",
            "LetThereBeSpace",
            "LetThereBeDeep",
            "RewriteRule",
        )

        universe = Universe(universe_id="snapshot-test")
        chronicle.replay(universe)

        self.assertEqual(
            universe.snapshot["word_replay_state"],
            {
                "light": True,
                "space": True,
                "chaos": False,
                "order": True,
                "deep": True,
                "rules_modified": True,
            },
        )

    def test_independent_replays_produce_equal_snapshots(self):
        chronicle = self.make_chronicle(
            "LetThereBeLight",
            "LetThereBeSpace",
        )

        first = Universe(universe_id="same-reality")
        second = Universe(universe_id="same-reality")

        chronicle.replay(first)
        chronicle.replay(second)

        self.assertEqual(
            first.snapshot,
            second.snapshot,
        )

    def test_different_word_histories_have_distinct_snapshots(self):
        first = Universe(universe_id="same-reality")
        second = Universe(universe_id="same-reality")

        self.make_chronicle(
            "LetThereBeLight"
        ).replay(first)

        self.make_chronicle(
            "LetThereBeDeep"
        ).replay(second)

        self.assertNotEqual(
            first.snapshot,
            second.snapshot,
        )

        self.assertTrue(
            first.snapshot["word_replay_state"]["light"]
        )
        self.assertTrue(
            second.snapshot["word_replay_state"]["deep"]
        )

    def test_snapshot_does_not_expose_mutable_runtime_state(self):
        universe = Universe(
            universe_id="snapshot-isolation"
        )

        self.make_chronicle(
            "LetThereBeLight"
        ).replay(universe)

        snapshot = universe.snapshot

        snapshot["word_replay_state"]["light"] = False

        self.assertTrue(universe.light)
        self.assertTrue(
            universe.snapshot["word_replay_state"]["light"]
        )


if __name__ == "__main__":
    unittest.main()
