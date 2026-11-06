import io
import random
import unittest
from contextlib import redirect_stdout

from core.word.chronicle import Chronicle
from core.word.word import Word
from universe.universe import Universe


SYMBOLIC_FLAGS = (
    "light",
    "space",
    "chaos",
    "order",
    "deep",
    "rules_modified",
)


class FixedEmptyChoice:
    def choice(self, possibilities):
        if "empty" not in possibilities:
            raise AssertionError(
                "Missing empty possibility."
            )
        return "empty"


class SymbolicQuantumReplayIntegrationTests(
    unittest.TestCase
):

    @staticmethod
    def make_chronicle(*names):
        chronicle = Chronicle()

        for name in names:
            chronicle.record(Word(name))

        return chronicle

    @staticmethod
    def symbolic_fingerprint(universe):
        return tuple(
            (name, getattr(universe, name, None))
            for name in SYMBOLIC_FLAGS
        )

    @staticmethod
    def quantum_fingerprint(universe):
        return {
            "clock": universe.quantum_state.to_dict(),
            "statistics": universe.statistics.public_state,
            "boxes": tuple(
                box.public_state
                for box in universe.quantum_boxes
            ),
            "ages": tuple(
                box.age_ticks
                for box in universe.quantum_boxes
            ),
        }

    @classmethod
    def combined_fingerprint(cls, universe):
        return {
            "symbolic": cls.symbolic_fingerprint(universe),
            "quantum": cls.quantum_fingerprint(universe),
        }

    def setUp(self):
        self.chronicle = self.make_chronicle(
            "LetThereBeLight",
            "LetThereBeSpace",
        )

        self.original_words = tuple(
            self.chronicle.all()
        )

        with redirect_stdout(io.StringIO()):
            self.source = Universe(
                universe_id="a11_source"
            )

            self.source.enable_quantum_layer()

            self.source.should_collapse_quantum_box = (
                lambda _box: False
            )

            self.chronicle.replay(self.source)

            self.source.create_quantum_box(
                box_id="a11_shared_box",
                rng=random.Random(31),
            )

            self.source.tick_quantum_unprotected()
            self.source.tick_quantum_unprotected()

    def restore(
        self,
        name,
        *,
        chronicle=None,
        box_events=None,
        clock_events=None,
        order="symbolic_first",
    ):
        if chronicle is None:
            chronicle = self.chronicle

        if box_events is None:
            box_events = tuple(
                self.source.quantum_events
            )

        if clock_events is None:
            clock_events = tuple(
                self.source.quantum_clock_events
            )

        with redirect_stdout(io.StringIO()):
            target = Universe(universe_id=name)
            target.enable_quantum_layer()

            target.should_collapse_quantum_box = (
                lambda _box: False
            )

            def replay_words():
                chronicle.replay(target)

            def replay_quantum():
                target.replay_quantum_history(
                    box_events=box_events,
                    clock_events=clock_events,
                    preserve_history=True,
                )

            if order == "symbolic_first":
                replay_words()
                replay_quantum()
            elif order == "quantum_first":
                replay_quantum()
                replay_words()
            else:
                raise ValueError(
                    "Unknown replay order."
                )

        return target

    def test_combined_replay_restores_both_scopes(self):
        first = self.restore("a11_first")
        second = self.restore("a11_second")

        expected = self.combined_fingerprint(
            self.source
        )

        self.assertEqual(
            self.combined_fingerprint(first),
            expected,
        )

        self.assertEqual(
            self.combined_fingerprint(second),
            expected,
        )

        self.assertEqual(
            first.quantum_lifecycle_timeline(),
            self.source.quantum_lifecycle_timeline(),
        )

        self.assertEqual(
            second.quantum_lifecycle_timeline(),
            self.source.quantum_lifecycle_timeline(),
        )

        self.assertIsNot(
            first.quantum_boxes[0],
            second.quantum_boxes[0],
        )

        self.assertIsNot(
            first.quantum_boxes[0],
            self.source.quantum_boxes[0],
        )

        self.assertIsNot(
            first.quantum_events[0],
            second.quantum_events[0],
        )

        self.assertEqual(
            tuple(self.chronicle.all()),
            self.original_words,
        )

    def test_replay_order_is_independent(self):
        words_first = self.restore(
            "a11_words_first",
            order="symbolic_first",
        )

        quantum_first = self.restore(
            "a11_quantum_first",
            order="quantum_first",
        )

        self.assertEqual(
            self.combined_fingerprint(words_first),
            self.combined_fingerprint(quantum_first),
        )

        self.assertEqual(
            words_first.quantum_lifecycle_timeline(),
            quantum_first.quantum_lifecycle_timeline(),
        )

        self.assertEqual(
            self.combined_fingerprint(words_first),
            self.combined_fingerprint(self.source),
        )

    def test_symbolic_divergence_keeps_quantum_equal(self):
        deep_history = self.make_chronicle(
            "LetThereBeLight",
            "LetThereBeSpace",
            "LetThereBeDeep",
        )

        rules_history = self.make_chronicle(
            "LetThereBeLight",
            "LetThereBeSpace",
            "RewriteRule",
        )

        parent_before = self.combined_fingerprint(
            self.source
        )

        deep_branch = self.restore(
            "a11_deep",
            chronicle=deep_history,
        )

        rules_branch = self.restore(
            "a11_rules",
            chronicle=rules_history,
        )

        self.assertNotEqual(
            self.symbolic_fingerprint(deep_branch),
            self.symbolic_fingerprint(rules_branch),
        )

        self.assertTrue(deep_branch.deep)
        self.assertTrue(rules_branch.rules_modified)

        self.assertIsNone(
            getattr(deep_branch, "rules_modified", None)
        )

        self.assertIsNone(
            getattr(rules_branch, "deep", None)
        )

        self.assertEqual(
            self.quantum_fingerprint(deep_branch),
            self.quantum_fingerprint(rules_branch),
        )

        self.assertEqual(
            deep_branch.quantum_lifecycle_timeline(),
            rules_branch.quantum_lifecycle_timeline(),
        )

        self.assertEqual(
            self.combined_fingerprint(self.source),
            parent_before,
        )

        self.assertEqual(
            tuple(self.chronicle.all()),
            self.original_words,
        )

    def test_quantum_divergence_keeps_symbolic_equal(self):
        parent_before = self.combined_fingerprint(
            self.source
        )

        parent_boxes = tuple(
            self.source.quantum_events
        )
        parent_clock = tuple(
            self.source.quantum_clock_events
        )

        left = self.restore("a11_left")
        right = self.restore("a11_right")

        with redirect_stdout(io.StringIO()):
            left.open_quantum_box(
                "a11_shared_box",
                rng=FixedEmptyChoice(),
            )

            right.create_quantum_box(
                box_id="a11_right_box",
                rng=random.Random(77),
            )

            left.tick_quantum_unprotected()
            right.tick_quantum_unprotected()

        self.assertEqual(
            self.symbolic_fingerprint(left),
            self.symbolic_fingerprint(right),
        )

        self.assertEqual(
            self.symbolic_fingerprint(left),
            self.symbolic_fingerprint(self.source),
        )

        self.assertNotEqual(
            self.quantum_fingerprint(left),
            self.quantum_fingerprint(right),
        )

        self.assertEqual(left.quantum_boxes, [])

        self.assertEqual(
            [box.id for box in right.quantum_boxes],
            ["a11_shared_box", "a11_right_box"],
        )

        self.assertEqual(
            [event.tick for event in left.quantum_clock_events],
            [1, 2, 3],
        )

        self.assertEqual(
            [event.tick for event in right.quantum_clock_events],
            [1, 2, 3],
        )

        for branch in (left, right):
            reconstructed = self.restore(
                branch.id + "_replayed",
                box_events=tuple(
                    branch.quantum_events
                ),
                clock_events=tuple(
                    branch.quantum_clock_events
                ),
                order="quantum_first",
            )

            self.assertEqual(
                self.combined_fingerprint(reconstructed),
                self.combined_fingerprint(branch),
            )

            self.assertEqual(
                reconstructed.quantum_lifecycle_timeline(),
                branch.quantum_lifecycle_timeline(),
            )

        self.assertEqual(
            self.combined_fingerprint(self.source),
            parent_before,
        )

        self.assertEqual(
            tuple(self.source.quantum_events),
            parent_boxes,
        )

        self.assertEqual(
            tuple(self.source.quantum_clock_events),
            parent_clock,
        )

        self.assertEqual(
            tuple(self.chronicle.all()),
            self.original_words,
        )


if __name__ == "__main__":
    unittest.main()
