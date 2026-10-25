import unittest

from meeting_place.dice_vial import (
    DiceVial,
    DiceVialSecretRotationEvent,
)


class FixedVialRng:
    def randint(self, minimum, maximum):
        return 7

    def choice(self, values):
        return list(values)[0]


class DiceVialObjectStateTests(unittest.TestCase):

    def test_roll_returns_stored_event_object(self):
        vial = DiceVial()

        event = vial.roll(rng=FixedVialRng())

        self.assertIsInstance(
            event,
            DiceVialSecretRotationEvent,
        )
        self.assertIs(
            event,
            vial.secret_event,
        )
        self.assertEqual(event.roll, 7)
        self.assertTrue(event.box_created)
        self.assertTrue(event.quantum_tick_requested)

        with self.assertRaises(TypeError):
            _ = event["roll"]

        snapshot = event.to_dict()
        snapshot["roll"] = 99

        self.assertEqual(event.roll, 7)

    def test_missing_universe_preserves_export(self):
        vial = DiceVial()

        snapshot = vial.resolve_missing_universe(
            rng=FixedVialRng()
        )

        self.assertEqual(
            snapshot["layer"],
            "multiverse",
        )
        self.assertEqual(
            snapshot["universe_id"],
            0,
        )
        self.assertIsInstance(
            snapshot["secret_event"],
            dict,
        )
        self.assertEqual(
            snapshot["secret_event"]["roll"],
            7,
        )

        snapshot["secret_event"]["roll"] = 99

        self.assertEqual(
            vial.secret_event.roll,
            7,
        )
