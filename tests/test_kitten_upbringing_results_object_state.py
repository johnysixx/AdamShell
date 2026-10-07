import unittest

from universe.universe import Universe

from cats.cat_family_system import (
    CatFamilySystem,
)
from cats.cat_maternal_care_result_state import (
    CatFosterUpbringingCareSyncedEvent,
    CatMaternalUpbringingCareSyncedEvent,
)
from cats.cat_maternal_care_system import (
    CatMaternalCareSystem,
)
from cats.cat_personality_state import (
    CatPersonalityExperienceAppliedResult,
)
from cats.cats import Cats
from cats.development_resolver import (
    CatDevelopmentResolver,
)
from cats.kitten_growth_state import (
    KittenGrowthAppliedEvent,
)
from cats.kitten_upbringing_phase import (
    KittenUpbringingPhase,
)
from cats.kitten_upbringing_resolver import (
    KittenUpbringingResolver,
)
from cats.kitten_upbringing_result_state import (
    KittenDailyCareEvent,
    KittenFamilyHuntEvent,
    KittenSocializationLessonEvent,
    KittenUpbringingDayCompletedEvent,
    KittenUpbringingDaySkippedResult,
)


class KittenUpbringingResultsObjectStateTests(
    unittest.TestCase
):

    def setUp(self):
        self.universe = Universe()

        self.cats = Cats(
            self.universe
        )

        self.development = (
            CatDevelopmentResolver(
                self.universe
            )
        )

        self.resolver = (
            KittenUpbringingResolver(
                self.universe
            )
        )

        self.mother = self.cats.create_cat(
            name="object_mother",
            color="black",
            fur_length="short",
            origin="natural_birth",
        )

        self.father = self.cats.create_cat(
            name="object_father",
            color="orange",
            fur_length="short",
            sex="male",
            origin="natural_birth",
        )

        self.kitten = self.cats.create_cat(
            name="object_kitten",
            color="white",
            fur_length="short",
            origin="kitten_birth_resolver",
        )

        self.kitten.family.parents.mother = (
            self.mother.name
        )

        self.kitten.family.parents.father = (
            self.father.name
        )

        self.kitten.mother_name = (
            self.mother.name
        )

        self.kitten.father_name = (
            self.father.name
        )

        CatFamilySystem(
            self.cats
        ).register_birth(
            mother=self.mother,
            kittens=[
                self.kitten
            ],
            cats=self.cats.cats,
        )

        self.development.initialize_newborn(
            self.kitten,
            birth_day=0,
        )

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

    def run_at_age(
        self,
        age_days,
    ):
        self.kitten.age_days = (
            age_days
        )

        return self.resolver.tick_day(
            kitten=self.kitten,
            cats=self.cats.cats,
            current_day=age_days,
        )

    def test_completed_day_is_object_with_object_events(
        self
    ):
        result = self.run_at_age(
            10
        )

        self.assertIsInstance(
            result,
            KittenUpbringingDayCompletedEvent,
        )

        self.assertTrue(
            result.processed
        )

        self.assertIs(
            result.phase,
            KittenUpbringingPhase.COMPLETE_MATERNAL_CARE,
        )

        self.assertIsInstance(
            result.events,
            tuple,
        )

        self.assertEqual(
            result.event_count,
            len(result.events),
        )

        self.assertFalse(
            any(
                isinstance(
                    event,
                    dict,
                )
                for event
                in result.events
            )
        )

        self.assert_object_only(
            result
        )

    def test_daily_care_and_maternal_sync_are_objects(
        self
    ):
        result = self.run_at_age(
            10
        )

        care_events = [
            event
            for event
            in result.events
            if isinstance(
                event,
                KittenDailyCareEvent,
            )
        ]

        self.assertEqual(
            len(care_events),
            4,
        )

        sync = next(
            event
            for event
            in result.events
            if isinstance(
                event,
                CatMaternalUpbringingCareSyncedEvent,
            )
        )

        self.assertTrue(
            sync.synced
        )

        self.assertEqual(
            sync.actions,
            (
                "nursing",
                "cleaning",
                "warming",
                "protection",
            ),
        )

        for event in [
            *care_events,
            sync,
        ]:
            self.assert_object_only(
                event
            )

    def test_maternal_sync_rejects_legacy_mapping_events(
        self
    ):
        care = CatMaternalCareSystem(
            self.cats
        )

        with self.assertRaises(
            TypeError
        ):
            care.record_upbringing_care(
                mother=self.mother,
                kitten=self.kitten,
                events=[
                    {
                        "name":
                            "fed_by_mother"
                    }
                ],
                age_days=5,
                current_day=5,
            )

    def test_foster_sync_is_object(
        self
    ):
        foster = self.cats.create_cat(
            name="object_foster",
            color="gray",
            fur_length="short",
            sex="female",
        )

        (
            self.kitten
            .maternal_care_received
            .foster_mother
        ) = foster.name

        event = KittenDailyCareEvent(
            name="fed_by_mother",
            kitten=self.kitten.name,
            mother=foster.name,
            age_days=5,
            day=5,
        )

        result = (
            CatMaternalCareSystem(
                self.cats
            )
            .record_foster_upbringing_care(
                foster_mother=foster,
                kitten=self.kitten,
                events=[
                    event
                ],
                age_days=5,
                current_day=5,
            )
        )

        self.assertIsInstance(
            result,
            CatFosterUpbringingCareSyncedEvent,
        )

        self.assertTrue(
            result.synced
        )

        self.assertEqual(
            result.actions,
            (
                "nursing",
            ),
        )

        self.assert_object_only(
            result
        )

    def test_socialization_contains_personality_object(
        self
    ):
        result = self.run_at_age(
            14
        )

        lesson = next(
            event
            for event
            in result.events
            if isinstance(
                event,
                KittenSocializationLessonEvent,
            )
        )

        self.assertIsInstance(
            lesson.personality,
            CatPersonalityExperienceAppliedResult,
        )

        self.assertTrue(
            lesson.personality.applied
        )

        self.assertAlmostEqual(
            self.kitten
            .personality
            .traits
            .empathy,
            0.51,
        )

        self.assert_object_only(
            lesson
        )

    def test_family_hunt_contains_growth_object(
        self
    ):
        self.run_at_age(
            35
        )

        result = self.run_at_age(
            36
        )

        hunt = next(
            event
            for event
            in result.events
            if isinstance(
                event,
                KittenFamilyHuntEvent,
            )
        )

        self.assertIsInstance(
            hunt.growth,
            KittenGrowthAppliedEvent,
        )

        self.assertTrue(
            hunt.growth.grew
        )

        self.assertIsInstance(
            hunt.teachers,
            tuple,
        )

        self.assert_object_only(
            hunt
        )

    def test_histories_store_detached_completed_wrappers(
        self
    ):
        result = self.run_at_age(
            10
        )

        resolver_event = (
            self.resolver.history[
                -1
            ]
        )

        kitten_event = (
            self.kitten
            .upbringing
            .history[
                -1
            ]
        )

        quantum_event = (
            self.universe
            .quantum_events[
                -1
            ]
        )

        for event in (
            resolver_event,
            kitten_event,
            quantum_event,
        ):
            self.assertIsInstance(
                event,
                KittenUpbringingDayCompletedEvent,
            )

            self.assertEqual(
                event,
                result,
            )

            self.assertIsNot(
                event,
                result,
            )

        self.assertIsNot(
            resolver_event,
            kitten_event,
        )

        self.assertIsNot(
            kitten_event,
            quantum_event,
        )

        self.assertIs(
            resolver_event.events,
            result.events,
        )

    def test_skip_result_is_object_and_history_is_detached(
        self
    ):
        manifested = (
            self.cats.create_cat(
                name="object_manifested",
                color="gray",
                fur_length="short",
                origin="dice_manifestation",
            )
        )

        result = self.resolver.tick_day(
            kitten=manifested,
            cats=self.cats.cats,
            current_day=1,
        )

        stored = (
            self.resolver.history[
                -1
            ]
        )

        self.assertIsInstance(
            result,
            KittenUpbringingDaySkippedResult,
        )

        self.assertFalse(
            result.processed
        )

        self.assertEqual(
            result.reason,
            "maternal_teaching_not_required",
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
            result
        )


if __name__ == "__main__":
    unittest.main()
