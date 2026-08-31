import unittest

from multiverse import UniverseRegistry
from universe.universe import Universe
from cats.cats import Cats
from cats.cat_learning import CatLearning
from cats.cat_emergency_lactation_system import (
    CatEmergencyLactationSystem
)
from cats.cat_maternal_care_system import (
    CatMaternalCareSystem
)
from cats.kitten_upbringing_resolver import (
    KittenUpbringingResolver
)
from meeting_place.meeting_place import (
    MeetingPlace
)


class CatEmergencyLactationSystemTests(
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

        self.rescuer = (
            self.cats.create_cat(
                name="foster_cat",
                color="black",
                fur_length="short",
                sex="female"
            )
        )

        self.rescuer.emergency_nursing.can_induce_lactation = (
            True
        )

        self.kitten = self._orphan(
            "orphan_kitten",
            age_days=10
        )

        self.system = (
            CatEmergencyLactationSystem(
                cats_layer=self.cats,
                meeting_place=self.bar
            )
        )

    def _orphan(
        self,
        name,
        age_days
    ):
        kitten = (
            self.cats.create_cat(
                name=name,
                color="black",
                fur_length="short"
            )
        )

        kitten.age_days = age_days
        kitten.developmental_stage = "kitten"

        kitten.mother_name = (
            "missing_mother"
        )

        kitten.parents = {
            "mother":
                "missing_mother",
            "father":
                None,
        }

        kitten.family.parents[
            "mother"
        ] = "missing_mother"

        kitten.learning = (
            CatLearning
            .create_newborn_state(
                mother_name=
                    "missing_mother"
            )
        )

        return kitten

    def test_capable_cat_brings_orphan_to_bar_and_induces_lactation(
        self
    ):
        result = (
            self.system
            .rescue_orphaned_kittens(
                rescuer=self.rescuer,
                kittens=[self.kitten],
                cats=self.cats.cats,
                current_day=10
            )
        )

        self.assertTrue(
            result["rescued"]
        )

        self.assertTrue(
            result[
                "lactation_induced"
            ]
        )

        self.assertEqual(
            self.kitten.current_layer,
            "meeting_place"
        )

        self.assertTrue(
            self.kitten
            .maternal_care_received
            .rescued_to_bar
        )

        self.assertEqual(
            self.kitten
            .maternal_care_received
            .foster_mother,
            self.rescuer.name
        )

        self.assertTrue(
            self.rescuer
            .emergency_nursing
            .induced_lactation
        )

        self.assertGreaterEqual(
            self.rescuer
            .emergency_nursing
            .garfield_consultations,
            1
        )

        self.assertGreaterEqual(
            self.kitten
            .maternal_care_received
            .foster_nursing_events,
            1
        )

    def test_cat_without_capability_cannot_induce_lactation(
        self
    ):
        self.rescuer.emergency_nursing.can_induce_lactation = (
            False
        )

        result = (
            self.system
            .rescue_orphaned_kittens(
                self.rescuer,
                [self.kitten],
                cats=self.cats.cats
            )
        )

        self.assertFalse(
            result["rescued"]
        )

        self.assertEqual(
            result["reason"],
            "cat_cannot_induce_lactation"
        )

    def test_present_biological_mother_prevents_orphan_rescue(
        self
    ):
        mother = (
            self.cats.create_cat(
                name="real_mother",
                color="white",
                fur_length="short"
            )
        )

        self.kitten.mother_name = (
            mother.name
        )

        self.kitten.parents[
            "mother"
        ] = mother.name

        self.kitten.family.parents[
            "mother"
        ] = mother.name

        result = (
            self.system
            .rescue_orphaned_kittens(
                self.rescuer,
                [self.kitten],
                cats=self.cats.cats
            )
        )

        self.assertFalse(
            result["rescued"]
        )

    def test_kitten_must_need_both_milk_and_teaching(
        self
    ):
        self.kitten.age_days = 60

        assessment = (
            self.system
            .needs_orphan_rescue(
                self.kitten,
                cats=self.cats.cats
            )
        )

        self.assertFalse(
            assessment["needs_milk"]
        )

        self.kitten.age_days = 10

        self.kitten.learning[
            "teaching_required"
        ] = False

        assessment = (
            self.system
            .needs_orphan_rescue(
                self.kitten,
                cats=self.cats.cats
            )
        )

        self.assertFalse(
            assessment[
                "needs_teaching"
            ]
        )

    def test_foster_mother_can_continue_maternal_care(
        self
    ):
        self.system.rescue_orphaned_kittens(
            self.rescuer,
            [self.kitten],
            cats=self.cats.cats,
            current_day=10
        )

        care = CatMaternalCareSystem(
            self.cats
        )

        result = (
            care.provide_foster_care(
                self.rescuer,
                self.kitten,
                age_days=11,
                current_day=11
            )
        )

        self.assertTrue(
            result["provided"]
        )

        self.assertIn(
            "nursing",
            result["actions"]
        )

    def test_upbringing_uses_foster_when_biological_mother_is_missing(
        self
    ):
        self.system.rescue_orphaned_kittens(
            self.rescuer,
            [self.kitten],
            cats=self.cats.cats
        )

        upbringing = (
            KittenUpbringingResolver(
                self.universe
            )
        )

        resolved = (
            upbringing._find_parent(
                self.kitten,
                self.cats.cats,
                "mother"
            )
        )

        self.assertIs(
            resolved,
            self.rescuer
        )

    def test_capability_assignment_is_deterministic(
        self
    ):
        first = (
            self.cats.create_cat(
                name=
                    "deterministic_candidate",
                color="black",
                fur_length="short",
                sex="female"
            )
        )

        other_universe = Universe()

        other_cats = Cats(
            other_universe
        )

        second = (
            other_cats.create_cat(
                name=
                    "deterministic_candidate",
                color="black",
                fur_length="short",
                sex="female"
            )
        )

        self.assertEqual(
            first
            .emergency_nursing
            .can_induce_lactation,
            second
            .emergency_nursing
            .can_induce_lactation
        )


if __name__ == "__main__":
    unittest.main()
