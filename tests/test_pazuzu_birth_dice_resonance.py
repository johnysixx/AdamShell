import unittest

from multiverse import UniverseRegistry
from universe.universe import Universe
from universe.bootstraps.universe_bootstrap import (
    UniverseBootstrap
)
from universe.bootstraps.entity_bootstrap import (
    EntityBootstrap
)


class FixedResonanceRng:

    def randint(self, minimum, maximum):
        return min(7, maximum)

    def choice(self, items):
        if "d12" in items:
            return "d12"

        return items[0]


class PazuzuBirthDiceResonanceTests(
    unittest.TestCase
):

    def setUp(self):
        self.registry = UniverseRegistry()
        self.universe = Universe()

        (
            self.root_transition,
            self.layers,
            self.idea_universe
        ) = UniverseBootstrap(
            self.registry,
            self.universe
        ).run()

        self.meeting = self.layers.get(
            "meeting"
        )

        self.meeting.welcome_cat_d20()

        prepared = (
            self.meeting
            .cat_d20_prepare_pazuzu_profile()
        )

        bootstrap = EntityBootstrap(
            self.universe,
            self.idea_universe,
            self.root_transition,
            pazuzu_profile=prepared[
                "profile"
            ]
        )

        bootstrap._create_pazuzu()

        self.pazuzu = bootstrap.pazuzu

    def test_pazuzu_birth_rotates_four_dice_sources(self):
        quantum_rolls_before = (
            self.universe.quantum_die.roll_count
        )

        result = (
            self.meeting
            .trigger_pazuzu_birth_dice_resonance(
                rng=FixedResonanceRng()
            )
        )

        self.assertTrue(
            result["triggered"]
        )

        self.assertEqual(
            self.pazuzu["name"],
            "pazuzu"
        )

        self.assertEqual(
            self.universe.quantum_die.roll_count,
            quantum_rolls_before + 1
        )

        self.assertEqual(
            result["quantum_d20"]["value"],
            7
        )

        self.assertTrue(
            result["cat_d20"]["turned"]
        )

        self.assertEqual(
            result["cat_d20"]["value"],
            7
        )

        self.assertEqual(
            result["dice_vial"]["name"],
            "dice_vial_secret_rotation"
        )

        self.assertEqual(
            result["dice_vial"]["roll"],
            7
        )

        self.assertTrue(
            result["dice_box"]["rotated"]
        )

        self.assertEqual(
            result["dice_box"]["die"],
            "d12"
        )

        self.assertEqual(
            result["dice_box"]["value"],
            7
        )

        self.assertLessEqual(
            result["dice_box"]["value"],
            result["dice_box"]["sides"]
        )

        self.assertFalse(
            result["dice_box"][
                "removed_from_box"
            ]
        )

        self.assertEqual(
            self.universe.quantum_events[-1][
                "name"
            ],
            "pazuzu_birth_dice_resonance"
        )

    def test_pazuzu_birth_resonance_runs_only_once(self):
        first = (
            self.meeting
            .trigger_pazuzu_birth_dice_resonance(
                rng=FixedResonanceRng()
            )
        )

        quantum_rolls_after_first = (
            self.universe.quantum_die.roll_count
        )

        cat_turns_after_first = len(
            self.meeting.cat_d20_secret_history
        )

        box_turns_after_first = len(
            self.meeting
            .dice_box
            .rotation_history
        )

        second = (
            self.meeting
            .trigger_pazuzu_birth_dice_resonance(
                rng=FixedResonanceRng()
            )
        )

        self.assertTrue(
            first["triggered"]
        )

        self.assertTrue(
            second["already_triggered"]
        )

        self.assertEqual(
            self.universe.quantum_die.roll_count,
            quantum_rolls_after_first
        )

        self.assertEqual(
            len(
                self.meeting
                .cat_d20_secret_history
            ),
            cat_turns_after_first
        )

        self.assertEqual(
            len(
                self.meeting
                .dice_box
                .rotation_history
            ),
            box_turns_after_first
        )

    def test_pazuzu_birth_resonance_is_wired_into_kernel(self):
        from multiverse.kernel import (
            MultiverseKernel
        )

        kernel = MultiverseKernel()

        kernel._initialize_multiverse()

        quantum_rolls_before = (
            kernel.universe
            .quantum_die
            .roll_count
        )

        kernel._initialize_entities()

        result = (
            kernel
            .pazuzu_birth_dice_resonance
        )

        self.assertEqual(
            [
                cat["name"]
                for cat
                in kernel.universe.cats_layer.cats
            ],
            [
                "cat_d20",
                "pazuzu"
            ]
        )

        self.assertTrue(
            result["triggered"]
        )

        self.assertEqual(
            kernel.universe
            .quantum_die
            .roll_count,
            quantum_rolls_before + 1
        )

        self.assertTrue(
            result["cat_d20"]["turned"]
        )

        self.assertEqual(
            result["dice_vial"]["name"],
            "dice_vial_secret_rotation"
        )

        self.assertTrue(
            result["dice_box"]["rotated"]
        )

        self.assertGreaterEqual(
            result["dice_box"]["value"],
            1
        )

        self.assertLessEqual(
            result["dice_box"]["value"],
            result["dice_box"]["sides"]
        )


if __name__ == "__main__":
    unittest.main()