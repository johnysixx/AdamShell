import unittest
from dataclasses import FrozenInstanceError
from types import SimpleNamespace

from meeting_place.bar_energy_entropy_service_state import (
    BarEnergyDrinkServiceResult,
    BarEntropyDrinkServiceResult,
)
from meeting_place.bar_service_effect_state import (
    BarGodEnergyDrinkEffect,
    BarGodEntropyDrinkEffect,
    BarIdeaEntityEnergyDrinkEffect,
    BarIdeaEntityEntropyDrinkEffect,
)
from meeting_place.meeting_place import MeetingPlace
from meeting_place.reservoir_event_state import (
    BarEnergySpentEvent,
    EntropyServedEvent,
)
from multiverse import UniverseRegistry
from universe.pre_cosmic_rules import (
    ENERGY_SERVING_J,
    ENTROPY_DRINK_UNITS,
)
from universe.universe import Universe


class BarEnergyEntropyServiceObjectStateTests(
    unittest.TestCase
):

    def _bar(self):
        universe = Universe()
        universe.universe_registry = UniverseRegistry()
        return MeetingPlace(universe)

    def _entity(self, entity_type):
        values = {
            "name": entity_type,
            "type": entity_type,
            "energy_j": 0.0,
            "existence_pct": 100.0,
            "creative_will": 1.0,
            "will": 1.0,
        }
        return SimpleNamespace(**values)

    def _assert_object_only(self, value):
        self.assertNotIsInstance(value, dict)

        for name in (
            "get", "keys", "items", "values",
            "__getitem__", "__setitem__",
        ):
            self.assertFalse(hasattr(value, name))

        with self.assertRaises(TypeError):
            _ = value["service_effect"]

        with self.assertRaises(FrozenInstanceError):
            value.service_effect = None

    def test_god_energy_service_returns_objects(self):
        bar = self._bar()
        god = self._entity("god")

        bar.energy_reservoir.add_energy(
            "test",
            ENERGY_SERVING_J * 2,
        )

        result = bar.serve_energy(god)

        self.assertIsInstance(
            result,
            BarEnergyDrinkServiceResult,
        )
        self.assertIsInstance(
            result.reservoir_event,
            BarEnergySpentEvent,
        )
        self.assertIsInstance(
            result.service_effect,
            BarGodEnergyDrinkEffect,
        )
        self.assertIs(
            result.reservoir_event,
            bar.energy_reservoir.events[-1],
        )
        self.assertGreater(god.creative_will, 1.0)
        self._assert_object_only(result)

    def test_idea_energy_service_returns_objects(self):
        bar = self._bar()
        idea = self._entity("idea_entity")

        bar.energy_reservoir.add_energy(
            "test",
            ENERGY_SERVING_J * 2,
        )

        result = bar.serve_energy(idea)

        self.assertIsInstance(
            result,
            BarEnergyDrinkServiceResult,
        )
        self.assertIsInstance(
            result.service_effect,
            BarIdeaEntityEnergyDrinkEffect,
        )
        self.assertLess(idea.existence_pct, 100.0)
        self.assertGreater(idea.will, 1.0)
        self._assert_object_only(result)

    def test_god_entropy_service_returns_objects(self):
        bar = self._bar()
        god = self._entity("god")

        bar.entropy_reservoir.add_entropy(
            "test",
            ENTROPY_DRINK_UNITS * 2,
        )

        result = bar.serve_entropy(god)

        self.assertIsInstance(
            result,
            BarEntropyDrinkServiceResult,
        )
        self.assertIsInstance(
            result.reservoir_event,
            EntropyServedEvent,
        )
        self.assertIsInstance(
            result.service_effect,
            BarGodEntropyDrinkEffect,
        )
        self.assertIs(
            result.reservoir_event,
            bar.entropy_reservoir.events[-1],
        )
        self.assertGreater(god.energy_j, 0.0)
        self.assertEqual(bar.total_entropy_served_ever, 1)
        self._assert_object_only(result)

    def test_idea_entropy_service_returns_objects(self):
        bar = self._bar()
        idea = self._entity("idea_entity")

        bar.entropy_reservoir.add_entropy(
            "test",
            ENTROPY_DRINK_UNITS * 2,
        )

        result = bar.serve_entropy(idea)

        self.assertIsInstance(
            result,
            BarEntropyDrinkServiceResult,
        )
        self.assertIsInstance(
            result.service_effect,
            BarIdeaEntityEntropyDrinkEffect,
        )
        self.assertGreater(idea.energy_j, 0.0)
        self._assert_object_only(result)

    def test_unavailable_services_keep_none_contract(self):
        bar = self._bar()

        human = self._entity("human")
        god = self._entity("god")

        self.assertIsNone(bar.serve_energy(human))
        self.assertIsNone(bar.serve_entropy(human))

        # Eligible entity, insufficient reserves.
        self.assertIsNone(bar.serve_energy(god))
        self.assertIsNone(bar.serve_entropy(god))

        self.assertEqual(
            bar.total_entropy_served_ever,
            0,
        )

    def test_result_types_reject_invalid_components(self):
        with self.assertRaises(TypeError):
            BarEnergyDrinkServiceResult(
                reservoir_event={},
                service_effect={},
            )

        with self.assertRaises(TypeError):
            BarEntropyDrinkServiceResult(
                reservoir_event={},
                service_effect={},
            )


if __name__ == "__main__":
    unittest.main()
