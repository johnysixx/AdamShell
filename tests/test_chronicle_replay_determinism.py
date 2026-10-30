import unittest
from unittest.mock import patch

from core.word.chronicle import Chronicle
from core.word.word import Word
from core.reality.divergence import DivergenceInjector


class RecordingUniverse:

    def __init__(self, universe_id):
        self.id = universe_id
        self.received = []

    def hear(self, word):
        self.received.append(word.name)


class ChronicleReplayDeterminismTests(unittest.TestCase):

    def test_replay_preserves_order_across_recipients(self):
        chronicle = Chronicle()
        chronicle.record(Word("LetThereBeLight"))
        chronicle.record(Word("LetThereBeSpace"))

        first = RecordingUniverse("first")
        second = RecordingUniverse("second")

        chronicle.replay(first)
        chronicle.replay(second)

        expected = [
            "LetThereBeLight",
            "LetThereBeSpace",
        ]

        self.assertEqual(first.received, expected)
        self.assertEqual(second.received, expected)
        self.assertEqual(
            [word.name for word in chronicle.all()],
            expected,
        )

    def test_divergence_at_end_appends_word(self):
        chronicle = Chronicle()
        chronicle.record(Word("LetThereBeLight"))

        with patch(
            "core.reality.divergence.Universe",
            RecordingUniverse,
        ):
            universe, branch = DivergenceInjector().inject(
                chronicle,
                RecordingUniverse("root"),
                1,
                Word("LetThereBeSpace"),
            )

        expected = [
            "LetThereBeLight",
            "LetThereBeSpace",
        ]

        self.assertEqual(
            [word.name for word in branch.all()],
            expected,
        )
        self.assertEqual(universe.received, expected)

    def test_empty_chronicle_accepts_initial_divergence(self):
        chronicle = Chronicle()

        with patch(
            "core.reality.divergence.Universe",
            RecordingUniverse,
        ):
            universe, branch = DivergenceInjector().inject(
                chronicle,
                RecordingUniverse("root"),
                0,
                Word("LetThereBeLight"),
            )

        self.assertEqual(
            [word.name for word in branch.all()],
            ["LetThereBeLight"],
        )
        self.assertEqual(
            universe.received,
            ["LetThereBeLight"],
        )
        self.assertEqual(chronicle.all(), [])


if __name__ == "__main__":
    unittest.main()
