import unittest
from types import SimpleNamespace
from unittest.mock import call, patch

from cats.cats import Cats
from universe.universe import Universe


class UniverseWorldCatsObjectStateTests(
    unittest.TestCase
):

    def test_aroma_decay_uses_canonical_cats_layer(self):
        universe = Universe()
        cats = Cats(universe)

        first = SimpleNamespace(name="first_cat")
        second = SimpleNamespace(name="second_cat")
        box = SimpleNamespace(name="quantum_box")

        cats.cats.extend((first, second))
        universe.quantum_boxes.append(box)

        with patch(
            "universe.universe.AromaResidue.decay"
        ) as decay:
            universe._tick_aroma_residues()

        self.assertEqual(
            decay.call_args_list,
            [
                call(box, ticks=1),
                call(first, ticks=1),
                call(second, ticks=1),
            ],
        )

        self.assertIs(universe.cats_layer, cats)
        self.assertIs(cats.cats, cats.cats_state.cats)

    def test_public_world_mapping_is_not_runtime_source(
        self
    ):
        universe = Universe()
        cats = Cats(universe)

        actual_cat = SimpleNamespace(
            name="actual_cat",
        )

        fake_cat = SimpleNamespace(
            name="fake_cat",
        )

        cats.cats.append(actual_cat)

        universe.world["cats"] = {
            "cats": [fake_cat],
        }

        with patch(
            "universe.universe.AromaResidue.decay"
        ) as decay:
            universe._tick_aroma_residues()

        decay.assert_called_once_with(
            actual_cat,
            ticks=1,
        )

        self.assertIs(
            universe.cats_layer,
            cats,
        )
        self.assertIs(
            cats.cats[0],
            actual_cat,
        )

    def test_world_mapping_does_not_create_cats_layer(
        self
    ):
        universe = Universe()

        universe.world["cats"] = {
            "cats": [
                SimpleNamespace(
                    name="unregistered_cat",
                ),
            ],
        }

        self.assertFalse(
            hasattr(universe, "cats_layer")
        )

        with patch(
            "universe.universe.AromaResidue.decay"
        ) as decay:
            universe._tick_aroma_residues()

        decay.assert_not_called()

        self.assertFalse(
            hasattr(universe, "cats_layer")
        )

    def test_invalid_cats_layer_is_rejected(self):
        universe = Universe()

        universe.cats_layer = {
            "cats": [],
        }

        with patch(
            "universe.universe.AromaResidue.decay"
        ) as decay:
            with self.assertRaises(TypeError):
                universe._tick_aroma_residues()

        decay.assert_not_called()

    def test_public_cats_registry_remains_available(
        self
    ):
        universe = Universe()
        cats = Cats(universe)

        boundary = universe.world["cats"]

        self.assertIsInstance(
            boundary,
            dict,
        )
        self.assertIs(
            boundary["cats"],
            cats.cats,
        )
        self.assertIs(
            universe.world["cats_state"],
            cats.cats_state,
        )

        cat = SimpleNamespace(
            name="shared_cat",
        )

        cats.cats.append(cat)

        self.assertIs(
            boundary["cats"][-1],
            cat,
        )


if __name__ == "__main__":
    unittest.main()
