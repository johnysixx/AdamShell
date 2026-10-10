import unittest

from meeting_place.cat_arrival_state import (
    CatBarArrivalResult,
)

from multiverse import UniverseRegistry
from universe.universe import Universe

from cats.cat_emergency_lactation_result_state import (
    CatEmergencyLactationAdviceEvent,
    CatOrphanRescueAssessment,
    CatOrphanRescueDeniedResult,
    CatOrphanRescueEvent,
    CatOrphanTransportEvent,
)
from cats.cat_emergency_lactation_system import (
    CatEmergencyLactationSystem,
)
from cats.cat_learning import CatLearning
from cats.cat_maternal_care_result_state import (
    CatFosterMaternalCareDeniedResult,
    CatFosterMaternalCareEvent,
)
from cats.cat_maternal_care_system import (
    CatMaternalCareSystem,
)
from cats.cats import Cats
from cats.development_resolver import (
    CatDevelopmentResolver,
)
from cats.garfield_training_system import (
    GarfieldTrainingSystem,
)
from meeting_place.meeting_place import (
    MeetingPlace,
)


class CatEmergencyLactationResultsObjectStateTests(
    unittest.TestCase
):

    def setUp(self):
        self.universe = Universe()

        self.universe.universe_registry = (
            UniverseRegistry()
        )

        self.cats = Cats(
            self.universe
        )

        self.bar = MeetingPlace(
            self.universe
        )

        self.rescuer = self.cats.create_cat(
            name="object_foster",
            color="black",
            fur_length="short",
            sex="female",
        )

        (
            self.rescuer
            .emergency_nursing
            .can_induce_lactation
        ) = True

        self.kitten = self._orphan(
            "object_orphan",
            age_days=10,
        )

        self.system = (
            CatEmergencyLactationSystem(
                cats_layer=self.cats,
                meeting_place=self.bar,
            )
        )

    def _orphan(
        self,
        name,
        age_days,
    ):
        kitten = self.cats.create_cat(
            name=name,
            color="white",
            fur_length="short",
        )

        kitten.age_days = age_days

        kitten.developmental_stage = (
            CatDevelopmentResolver
            .stage_for_age(
                age_days
            )
        )

        kitten.mother_name = (
            "missing_mother"
        )

        kitten.family.parents.mother = (
            "missing_mother"
        )

        kitten.family.parents.father = None

        kitten.learning = (
            CatLearning
            .create_newborn_state(
                mother_name=
                    "missing_mother"
            )
        )

        return kitten

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

    def test_orphan_assessment_is_object(
        self
    ):
        result = (
            self.system
            .needs_orphan_rescue(
                self.kitten,
                cats=self.cats.cats,
            )
        )

        self.assertIsInstance(
            result,
            CatOrphanRescueAssessment,
        )

        self.assertTrue(
            result.orphan_rescue_needed
        )

        self.assertTrue(
            result.needs_milk
        )

        self.assertTrue(
            result.needs_teaching
        )

        self.assert_object_only(
            result
        )

    def test_rescue_denial_is_object(
        self
    ):
        (
            self.rescuer
            .emergency_nursing
            .can_induce_lactation
        ) = False

        result = (
            self.system
            .rescue_orphaned_kittens(
                self.rescuer,
                [self.kitten],
                cats=self.cats.cats,
            )
        )

        self.assertIsInstance(
            result,
            CatOrphanRescueDeniedResult,
        )

        self.assertFalse(
            result.rescued
        )

        self.assertEqual(
            result.reason,
            "cat_cannot_induce_lactation",
        )

        self.assert_object_only(
            result
        )

    def test_rescue_success_has_object_only_graph(
        self
    ):
        result = (
            self.system
            .rescue_orphaned_kittens(
                self.rescuer,
                [self.kitten],
                cats=self.cats.cats,
                current_day=10,
            )
        )

        self.assertIsInstance(
            result,
            CatOrphanRescueEvent,
        )

        self.assertTrue(
            result.rescued
        )

        self.assertTrue(
            result.lactation_induced
        )

        self.assertIsInstance(
            result.transport,
            CatOrphanTransportEvent,
        )

        self.assertGreaterEqual(
            len(
                result.transport.arrivals
            ),
            2,
        )

        for arrival in (
            result.transport.arrivals
        ):
            self.assertIsInstance(
                arrival,
                CatBarArrivalResult,
            )

            self.assert_object_only(
                arrival
            )

        self.assertIsInstance(
            result.garfield_advice,
            CatEmergencyLactationAdviceEvent,
        )

        self.assertIsInstance(
            result.foster_events,
            tuple,
        )

        self.assertEqual(
            len(
                result.foster_events
            ),
            1,
        )

        self.assertIsInstance(
            result.foster_events[0],
            CatFosterMaternalCareEvent,
        )

        for value in (
            result,
            result.transport,
            result.garfield_advice,
            result.foster_events[0],
        ):
            self.assert_object_only(
                value
            )

    def test_rescue_history_and_emit_are_detached_objects(
        self
    ):
        result = (
            self.system
            .rescue_orphaned_kittens(
                self.rescuer,
                [self.kitten],
                cats=self.cats.cats,
                current_day=10,
            )
        )

        history_event = (
            self.system.history[-1]
        )

        emitted = (
            self.cats.events[-1]
        )

        for event in (
            history_event,
            emitted,
        ):
            self.assertIsInstance(
                event,
                CatOrphanRescueEvent,
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
            history_event,
            emitted,
        )

    def test_garfield_advice_is_typed_snapshot(
        self
    ):
        result = (
            GarfieldTrainingSystem()
            .advise_emergency_lactation(
                self.rescuer,
                [self.kitten],
            )
        )

        stored = (
            self.rescuer
            .emergency_nursing
            .last_advice
        )

        interaction = (
            self.rescuer
            .social_interactions[-1]
        )

        self.assertIsInstance(
            result,
            CatEmergencyLactationAdviceEvent,
        )

        self.assertIsInstance(
            result.advice,
            tuple,
        )

        for event in (
            stored,
            interaction,
        ):
            self.assertIsInstance(
                event,
                CatEmergencyLactationAdviceEvent,
            )

            self.assertEqual(
                event,
                result,
            )

            self.assertIsNot(
                event,
                result,
            )

            self.assert_object_only(
                event
            )

    def test_foster_care_denial_is_object(
        self
    ):
        care = CatMaternalCareSystem(
            self.cats
        )

        result = care.provide_foster_care(
            self.rescuer,
            self.kitten,
            age_days=10,
        )

        self.assertIsInstance(
            result,
            CatFosterMaternalCareDeniedResult,
        )

        self.assertFalse(
            result.provided
        )

        self.assertEqual(
            result.reason,
            "foster_relationship_not_active",
        )

        self.assert_object_only(
            result
        )

    def test_foster_care_event_is_detached_object(
        self
    ):
        self.system.rescue_orphaned_kittens(
            self.rescuer,
            [self.kitten],
            cats=self.cats.cats,
            current_day=10,
        )

        care = CatMaternalCareSystem(
            self.cats
        )

        result = care.provide_foster_care(
            self.rescuer,
            self.kitten,
            age_days=11,
            current_day=11,
        )

        foster_event = (
            self.rescuer
            .social_interactions[-1]
        )

        kitten_event = (
            self.kitten
            .social_interactions[-1]
        )

        emitted = (
            self.cats.events[-1]
        )

        self.assertIsInstance(
            result,
            CatFosterMaternalCareEvent,
        )

        self.assertIsInstance(
            result.actions,
            tuple,
        )

        for event in (
            foster_event,
            kitten_event,
            emitted,
        ):
            self.assertIsInstance(
                event,
                CatFosterMaternalCareEvent,
            )

            self.assertEqual(
                event,
                result,
            )

            self.assertIsNot(
                event,
                result,
            )

            self.assert_object_only(
                event
            )

        self.assertIsNot(
            foster_event,
            kitten_event,
        )


if __name__ == "__main__":
    unittest.main()
