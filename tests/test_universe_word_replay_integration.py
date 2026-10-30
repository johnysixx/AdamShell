import unittest

from core.word.word import Word
from core.word.chronicle import Chronicle
from core.reality.fork import Fork
from core.reality.divergence import DivergenceInjector
from universe.universe import Universe


SYMBOLIC_FLAGS = (
    "light",
    "space",
    "chaos",
    "order",
    "deep",
    "rules_modified",
)


def symbolic_state(universe):
    return tuple(
        (name, getattr(universe, name, None))
        for name in SYMBOLIC_FLAGS
    )


class UniverseWordReplayIntegrationTests(unittest.TestCase):

    def make_chronicle(self, *names):
        chronicle = Chronicle()

        for name in names:
            chronicle.record(Word(name))

        return chronicle

    def test_real_universe_replay_is_deterministic(self):
        chronicle = self.make_chronicle(
            "LetThereBeLight",
            "LetThereBeSpace",
            "LetThereBeDeep",
            "RewriteRule",
        )

        original_words = tuple(chronicle.all())

        first = Universe(universe_id="replay-test")
        second = Universe(universe_id="replay-test")

        chronicle.replay(first)
        chronicle.replay(second)

        self.assertIsNot(first, second)
        self.assertEqual(
            symbolic_state(first),
            symbolic_state(second),
        )

        self.assertEqual(
            dict(symbolic_state(first)),
            {
                "light": True,
                "space": True,
                "chaos": False,
                "order": True,
                "deep": True,
                "rules_modified": True,
            },
        )

        self.assertEqual(
            tuple(chronicle.all()),
            original_words,
        )

    def test_replay_is_idempotent_for_symbolic_flags(self):
        chronicle = self.make_chronicle(
            "LetThereBeLight",
            "LetThereBeSpace",
        )

        universe = Universe(
            universe_id="idempotence-test"
        )

        chronicle.replay(universe)
        first_state = symbolic_state(universe)

        chronicle.replay(universe)
        second_state = symbolic_state(universe)

        self.assertEqual(
            first_state,
            second_state,
        )
        self.assertTrue(universe.light)
        self.assertTrue(universe.space)

    def test_fork_does_not_mutate_parent(self):
        chronicle = self.make_chronicle(
            "LetThereBeLight",
            "LetThereBeDeep",
        )

        parent = Universe(
            universe_id="parent-test"
        )
        parent_before = symbolic_state(parent)

        child, timeline = Fork().create(
            chronicle,
            parent,
        )

        self.assertIsNot(child, parent)
        self.assertEqual(
            timeline.parent_id,
            parent.id,
        )
        self.assertEqual(
            child.id,
            "parent-test-fork",
        )

        self.assertEqual(
            symbolic_state(parent),
            parent_before,
        )

        self.assertTrue(child.light)
        self.assertTrue(child.deep)

    def test_divergence_preserves_source(self):
        chronicle = self.make_chronicle(
            "LetThereBeLight",
            "LetThereBeSpace",
        )

        parent = Universe(
            universe_id="divergence-test"
        )

        original_words = tuple(chronicle.all())
        parent_before = symbolic_state(parent)

        branch_universe, branch = (
            DivergenceInjector().inject(
                chronicle,
                parent,
                1,
                Word("LetThereBeDeep"),
            )
        )

        self.assertEqual(
            [word.name for word in branch.all()],
            [
                "LetThereBeLight",
                "LetThereBeDeep",
            ],
        )

        self.assertEqual(
            tuple(chronicle.all()),
            original_words,
        )
        self.assertEqual(
            symbolic_state(parent),
            parent_before,
        )

        self.assertTrue(branch_universe.light)
        self.assertTrue(branch_universe.deep)
        self.assertIsNone(
            getattr(branch_universe, "space", None)
        )


if __name__ == "__main__":
    unittest.main()
