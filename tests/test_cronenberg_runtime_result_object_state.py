import unittest

from core.entity.cronenberg_system.growth import CronenbergGrowth
from core.entity.cronenberg_system.hunger import CronenbergHunger
from core.entity.cronenberg_system.metabolism import CronenbergMetabolism
from core.entity.cronenberg_system.result_state import (
    CronenbergDigestionStartedEvent,
    CronenbergEnergyReceivedEvent,
    CronenbergGrowthResult,
    CronenbergHungerDayResult,
    CronenbergLayerCrossedResult,
    CronenbergTravelStepResult,
)
from core.entity.cronenberg_system.travel import CronenbergTravel


class CronenbergRuntimeResultObjectStateTests(unittest.TestCase):

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
            _ = value["state"]

    def test_travel_results_are_objects(self):
        travel = CronenbergTravel()

        crossed = travel.cross_layer(1.0)
        step = travel.travel_step(
            size=1.0,
            available_energy=2.0,
        )

        self.assertIsInstance(
            crossed,
            CronenbergLayerCrossedResult,
        )
        self.assertIsInstance(
            step,
            CronenbergTravelStepResult,
        )
        self.assert_object_only(crossed)
        self.assert_object_only(step)

    def test_growth_results_are_objects(self):
        growth = CronenbergGrowth()

        results = (
            growth.grow_from_feeding(1.0),
            growth.grow_from_layer(1.0),
            growth.apply_starvation(
                size=1.0,
                hungry_days=2,
            ),
            growth.absorb_mass(
                size=1.0,
                consumed_mass=0.5,
            ),
        )

        for result in results:
            self.assertIsInstance(
                result,
                CronenbergGrowthResult,
            )
            self.assert_object_only(result)

    def test_hunger_results_are_objects(self):
        hunger = CronenbergHunger()

        day = hunger.finish_day(
            fed_enough=False
        )
        digestion = hunger.start_digestion(
            consumed_mass=1.5
        )

        self.assertIsInstance(
            day,
            CronenbergHungerDayResult,
        )
        self.assertIsInstance(
            digestion,
            CronenbergDigestionStartedEvent,
        )
        self.assert_object_only(day)
        self.assert_object_only(digestion)

    def test_metabolism_result_is_object(self):
        metabolism = CronenbergMetabolism()

        result = metabolism.receive_energy(
            amount=2.0,
            size=1.5,
        )

        self.assertIsInstance(
            result,
            CronenbergEnergyReceivedEvent,
        )
        self.assert_object_only(result)


if __name__ == "__main__":
    unittest.main()
