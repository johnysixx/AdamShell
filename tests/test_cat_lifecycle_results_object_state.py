import unittest

from universe.universe import Universe

from cats.cat_lifecycle import (
    CatLifeCycleHandler,
)
from cats.cat_lifecycle_result_state import (
    CatLifeCycleDayCompletedEvent,
)
from cats.cats import Cats
from cats.development_resolver import (
    CatAgeAdvancedEvent,
    CatDevelopmentResolver,
)
from cats.estrous_cycle_resolver import (
    CatEstrousCycleEvent,
)
from cats.mating_pregnancy_event import (
    CatPregnancyAdvancedEvent,
)
from cats.kitten_upbringing_result_state import (
    KittenUpbringingDayCompletedEvent,
)


class EmptyUniverse:

    cats_layer = None


class CatLifeCycleResultsObjectStateTests(
    unittest.TestCase
):

    def assert_object_only(
        self,
        value,
    ):
        for mapping_method in (
            "get",
            "keys",
            "items",
            "values",
            "to_dict",
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
            _ = value[
                "name"
            ]

    def test_empty_lifecycle_result_is_object(
        self
    ):
        handler = CatLifeCycleHandler(
            EmptyUniverse()
        )

        result = handler.tick_day(
            day=1
        )

        self.assertIsInstance(
            result,
            CatLifeCycleDayCompletedEvent,
        )

        self.assertEqual(
            result.cats_processed,
            0,
        )

        self.assertEqual(
            result.age_advances,
            (),
        )

        self.assertEqual(
            result.estrous_cycle_results,
            (),
        )

        self.assertEqual(
            result.pregnancy_advances,
            (),
        )

        self.assertEqual(
            result.births,
            (),
        )

        self.assertEqual(
            result.upbringing_results,
            (),
        )

        self.assert_object_only(
            result
        )

    def test_biological_cat_results_stay_objects(
        self
    ):
        universe = Universe()

        cats = Cats(
            universe
        )

        universe.start_big_bang()

        kitten = cats.create_cat(
            name="lifecycle_kitten",
            color="black",
            fur_length="short",
            sex="female",
            origin="kitten_birth_resolver",
        )

        kitten.mother_name = (
            "missing_mother"
        )

        kitten.family.parents.mother = (
            "missing_mother"
        )

        CatDevelopmentResolver(
            universe
        ).initialize_newborn(
            kitten,
            birth_day=0,
        )

        handler = (
            universe
            .cat_life_cycle_handler
        )

        result = handler.tick_day(
            day=1
        )

        self.assertIsInstance(
            result,
            CatLifeCycleDayCompletedEvent,
        )

        self.assertEqual(
            result.cats_processed,
            1,
        )

        self.assertIsInstance(
            result.age_advances,
            tuple,
        )

        self.assertIsInstance(
            result.age_advances[0],
            CatAgeAdvancedEvent,
        )

        self.assertIsInstance(
            result.estrous_cycle_results[0],
            CatEstrousCycleEvent,
        )

        self.assertIsInstance(
            result.upbringing_results[0],
            KittenUpbringingDayCompletedEvent,
        )

        self.assertFalse(
            any(
                isinstance(
                    item,
                    dict,
                )
                for collection in (
                    result.age_advances,
                    result.estrous_cycle_results,
                    result.upbringing_results,
                )
                for item in collection
            )
        )

    def test_pregnancy_advance_stays_object(
        self
    ):
        universe = Universe()

        cats = Cats(
            universe
        )

        universe.start_big_bang()

        mother = cats.create_cat(
            name="pregnant_cat",
            color="black",
            fur_length="short",
            sex="female",
        )

        reproduction = (
            mother.reproduction
        )

        reproduction.pregnant = True
        reproduction.pregnancy_day = 10
        reproduction.gestation_days = 65

        result = (
            universe
            .cat_life_cycle_handler
            .tick_day(
                day=11
            )
        )

        self.assertEqual(
            len(
                result.pregnancy_advances
            ),
            1,
        )

        self.assertIsInstance(
            result.pregnancy_advances[0],
            CatPregnancyAdvancedEvent,
        )

        self.assertEqual(
            result.pregnancy_advances[0]
            .pregnancy_day,
            11,
        )

    def test_history_stores_detached_wrapper(
        self
    ):
        handler = CatLifeCycleHandler(
            EmptyUniverse()
        )

        result = handler.tick_day(
            day=4
        )

        stored = (
            handler.history[-1]
        )

        self.assertIsInstance(
            stored,
            CatLifeCycleDayCompletedEvent,
        )

        self.assertEqual(
            stored,
            result,
        )

        self.assertIsNot(
            stored,
            result,
        )

        self.assert_object_only(
            stored
        )

    def test_mapping_child_is_rejected(
        self
    ):
        with self.assertRaises(
            TypeError
        ):
            CatLifeCycleDayCompletedEvent(
                day=1,
                cats_processed=1,
                age_advances=(
                    {
                        "name":
                            "cat_age_advanced"
                    },
                ),
                estrous_cycle_results=(),
                pregnancy_advances=(),
                births=(),
                upbringing_results=(),
            )


if __name__ == "__main__":
    unittest.main()
