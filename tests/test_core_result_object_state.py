import unittest

from core.actualization.possibility import (
    Possibility,
    PossibilityActualizedEvent,
)
from core.reality.compare import (
    RealityComparison,
    RealityDifference,
)
from core.word.chronicle import Chronicle
from core.word.word import Word


class CoreResultObjectStateTests(unittest.TestCase):

    def assert_object_only(self, value):
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
            _ = value["name"]

    def test_possibility_without_action_returns_object_event(self):
        result = Possibility(
            name="default_actualization",
            probability=1.0,
        ).actualize()

        self.assertIsInstance(
            result,
            PossibilityActualizedEvent,
        )
        self.assertEqual(
            result.name,
            "default_actualization",
        )
        self.assert_object_only(result)

    def test_reality_comparison_returns_difference_objects(self):
        first = Chronicle()
        second = Chronicle()
        first.record(Word("alpha"))
        second.record(Word("beta"))

        differences = RealityComparison().compare(
            first,
            second,
        )

        self.assertEqual(len(differences), 1)
        difference = differences[0]

        self.assertIsInstance(
            difference,
            RealityDifference,
        )
        self.assertEqual(difference.index, 0)
        self.assertEqual(difference.a, "alpha")
        self.assertEqual(difference.b, "beta")
        self.assert_object_only(difference)


if __name__ == "__main__":
    unittest.main()
