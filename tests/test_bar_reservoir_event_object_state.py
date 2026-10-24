import unittest

from meeting_place.reservoir_event_state import (
    BarEnergyAddedEvent,
    BarEnergySpentEvent,
    BarEntropyAddedEvent,
    EntropyServedEvent,
    QuantumEntropyTickEvent,
)
from meeting_place.reservoirs import (
    BarEnergyReservoir,
    BarEntropyReservoir,
)
from universe.pre_cosmic_rules import (
    ENTROPY_DRINK_UNITS,
)


class FixedEntropyRng:

    def __init__(
        self,
        value,
    ):
        self.value = float(
            value
        )

    def uniform(
        self,
        minimum,
        maximum,
    ):
        return self.value


class BarReservoirEventObjectStateTests(
    unittest.TestCase
):

    def _assert_object_only(
        self,
        event,
        key,
    ):
        for mapping_method in (
            "get",
            "keys",
            "items",
            "values",
            "setdefault",
        ):
            self.assertFalse(
                hasattr(
                    event,
                    mapping_method,
                )
            )

        with self.assertRaises(
            TypeError
        ):
            _ = event[
                key
            ]

    def test_energy_history_is_object_state(
        self
    ):
        reservoir = BarEnergyReservoir()

        added = reservoir.add_energy(
            "test_source",
            4.0,
        )

        spent = reservoir.spend_energy(
            "test_purpose",
            1.5,
        )

        self.assertIsInstance(
            added,
            BarEnergyAddedEvent,
        )

        self.assertIsInstance(
            spent,
            BarEnergySpentEvent,
        )

        self.assertEqual(
            len(reservoir.events),
            2,
        )

        self.assertIs(
            added,
            reservoir.events[0],
        )

        self.assertIs(
            spent,
            reservoir.events[1],
        )

        self.assertEqual(
            added.amount_j,
            4.0,
        )

        self.assertEqual(
            spent.amount_j,
            1.5,
        )

        self.assertEqual(
            spent.total_energy_j,
            2.5,
        )

        self._assert_object_only(
            added,
            "amount_j",
        )

        self._assert_object_only(
            spent,
            "purpose",
        )

        self.assertFalse(
            hasattr(
                added,
                "to_dict",
            )
        )

        self.assertFalse(
            hasattr(
                spent,
                "to_dict",
            )
        )

        public_state = (
            reservoir.public_state
        )

        self.assertIsInstance(
            public_state["events"][0],
            dict,
        )

        self.assertEqual(
            public_state[
                "events"
            ][0][
                "amount_j"
            ],
            4.0,
        )

        public_state[
            "events"
        ][0][
            "amount_j"
        ] = 123.0

        self.assertEqual(
            added.amount_j,
            4.0,
        )

    def test_entropy_history_is_object_state(
        self
    ):
        entropy = BarEntropyReservoir()
        energy = BarEnergyReservoir()

        tick = entropy.quantum_tick(
            rng=FixedEntropyRng(
                0.125
            )
        )

        added = entropy.add_entropy(
            "test_source",
            ENTROPY_DRINK_UNITS
            + 1.0,
        )

        served = entropy.serve_entropy(
            energy,
            "test_drinker",
        )

        self.assertIsInstance(
            tick,
            QuantumEntropyTickEvent,
        )

        self.assertIsInstance(
            added,
            BarEntropyAddedEvent,
        )

        self.assertIsInstance(
            served,
            EntropyServedEvent,
        )

        self.assertEqual(
            len(entropy.events),
            3,
        )

        self.assertIs(
            tick,
            entropy.events[0],
        )

        self.assertIs(
            added,
            entropy.events[1],
        )

        self.assertIs(
            served,
            entropy.events[2],
        )

        self.assertEqual(
            tick.amount_units,
            0.125,
        )

        self.assertEqual(
            added.source,
            "test_source",
        )

        self.assertEqual(
            served.drinker,
            "test_drinker",
        )

        self.assertGreater(
            served.entity_energy_gain_j,
            0.0,
        )

        self.assertIsInstance(
            energy.events[-1],
            BarEnergyAddedEvent,
        )

        self._assert_object_only(
            tick,
            "amount_units",
        )

        self._assert_object_only(
            added,
            "source",
        )

        self._assert_object_only(
            served,
            "drinker",
        )

        for event in (
            tick,
            added,
            served,
        ):
            self.assertFalse(
                hasattr(
                    event,
                    "to_dict",
                )
            )

        public_state = (
            entropy.public_state
        )

        self.assertEqual(
            [
                event["name"]
                for event
                in public_state["events"]
            ],
            [
                "quantum_entropy_tick",
                "bar_entropy_added",
                "entropy_served",
            ],
        )

        public_state[
            "events"
        ][-1][
            "drinker"
        ] = "changed"

        self.assertEqual(
            served.drinker,
            "test_drinker",
        )


if __name__ == "__main__":
    unittest.main()
