import unittest

from multiverse import UniverseRegistry
from universe.universe import Universe
from universe.bootstraps.universe_bootstrap import (
    UniverseBootstrap
)
from universe.bootstraps.entity_bootstrap import (
    EntityBootstrap
)
from core.entity.quantum_die import (
    QuantumDieRollEvent,
)
from meeting_place.bar_objects import (
    CatD20TurnEvent,
)
from meeting_place.dice_box import (
    DiceBoxRotationEvent,
)
from meeting_place.dice_vial import (
    DiceVialSecretRotationEvent,
)
from meeting_place.pazuzu_birth_dice_resonance_state import (
    PazuzuBirthDiceResonanceEvent,
    PazuzuCatD20ResonanceTurn,
)
from quantum.quantum_die_resolver import (
    QuantumDieResolutionEvent,
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
            pazuzu_profile=prepared.profile
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
            self.pazuzu.name,
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

        stored = (
            self.meeting
            .pazuzu_birth_dice_resonance_event
        )

        secret = (
            self.meeting
            .cat_d20_secret_history[-1]
        )

        quantum = (
            self.universe
            .quantum_events[-1]
        )

        self.assertIsInstance(
            stored,
            PazuzuBirthDiceResonanceEvent,
        )

        self.assertIsInstance(
            secret,
            PazuzuBirthDiceResonanceEvent,
        )

        self.assertIsInstance(
            quantum,
            PazuzuBirthDiceResonanceEvent,
        )

        self.assertIsInstance(
            stored.quantum_d20,
            QuantumDieRollEvent,
        )

        self.assertIsInstance(
            stored.quantum_resolution,
            QuantumDieResolutionEvent,
        )

        self.assertIsInstance(
            stored.cat_d20,
            PazuzuCatD20ResonanceTurn,
        )

        self.assertIsInstance(
            stored.cat_d20.turn,
            CatD20TurnEvent,
        )

        self.assertIsInstance(
            stored.dice_vial,
            DiceVialSecretRotationEvent,
        )

        self.assertIsInstance(
            stored.dice_box,
            DiceBoxRotationEvent,
        )

        self.assertIsInstance(
            self.meeting
            .dice_vial
            .secret_event,
            DiceVialSecretRotationEvent,
        )

        self.assertEqual(
            quantum.name,
            "pazuzu_birth_dice_resonance"
        )

        for value, key in (
            (
                stored,
                "triggered",
            ),
            (
                stored.cat_d20,
                "turn",
            ),
            (
                stored.dice_vial,
                "roll",
            ),
        ):
            for mapping_method in (
                "get",
                "keys",
                "items",
                "values",
            ):
                self.assertFalse(
                    hasattr(
                        value,
                        mapping_method,
                    )
                )

            with self.assertRaises(
                TypeError
            ):
                _ = value[key]

        result[
            "dice_vial"
        ][
            "roll"
        ] = 1

        self.assertEqual(
            stored.dice_vial.roll,
            7
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
                cat.name
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

        dice_box_result = result[
            "dice_box"
        ]

        self.assertGreaterEqual(
            dice_box_result["raw_value"],
            1
        )

        self.assertLessEqual(
            dice_box_result["raw_value"],
            dice_box_result["sides"]
        )

        if dice_box_result.get(
            "is_percentile",
            False
        ):
            self.assertIn(
                dice_box_result["value"],
                range(0, 100, 10)
            )

        else:
            self.assertEqual(
                dice_box_result["value"],
                dice_box_result["raw_value"]
            )


if __name__ == "__main__":
    unittest.main()