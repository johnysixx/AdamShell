from cats.cat_estrous_phase import CatEstrousPhase
import unittest

from cats import Cats

from cats.kitten_embryo_resolver import (
    KittenEmbryoCreatedEvent,
    KittenEmbryoResult,
)

from cats.kitten_viability_resolver import (
    KittenGeneticViabilityResult,
)

from cats.mating_pregnancy_event import (
    CatPregnancyPaternityResult,
    CatPregnancyStartedEvent,
)

from cats.mating_resolver import (
    CatMatingResolver,
)

from cats.paternity_resolver import (
    KittenFatherSelectedEvent,
)

from universe.universe import Universe


class FirstChoiceRng:

    def choice(
        self,
        values
    ):
        return list(
            values
        )[0]

    def randint(
        self,
        minimum,
        maximum
    ):
        return minimum

    def random(self):
        return 0.5


class CatPregnancyStartedObjectStateTests(
    unittest.TestCase
):

    def setUp(self):
        self.universe = Universe()
        self.universe.start_big_bang()

        self.cats = Cats(
            self.universe
        )

        self.female = (
            self.cats.create_cat(
                name="mother",
                color="black",
                fur_length="short",
                sex="female",
            )
        )

        self.male = (
            self.cats.create_cat(
                name="father",
                color="orange",
                fur_length="long",
                sex="male",
            )
        )

        self.female.reproduction.ovulation_threshold = 1
        self.female.reproduction.estrus_active = True
        self.female.reproduction.estrous_phase = CatEstrousPhase.ESTRUS

        self.resolver = (
            CatMatingResolver(
                self.universe
            )
        )

        self.resolver.mate(
            self.female,
            self.male,
            current_day=10,
        )

    def _start_pregnancy(self):
        return (
            self.resolver
            .close_mating_window(
                self.female,
                current_day=11,
                embryo_count=1,
                rng=FirstChoiceRng(),
            )
        )

    def test_history_reuses_existing_domain_events(
        self
    ):
        result = (
            self._start_pregnancy()
        )

        event = (
            self.resolver
            .history[-1]
        )

        paternity = (
            event
            .paternity_results[0]
        )

        embryo = (
            event
            .embryo_results[0]
        )

        self.assertIsInstance(
            result,
            CatPregnancyStartedEvent,
        )

        self.assertIs(
            result,
            event,
        )

        self.assertIsInstance(
            paternity,
            CatPregnancyPaternityResult,
        )

        self.assertFalse(
            hasattr(
                paternity,
                "to_dict",
            )
        )

        self.assertIsInstance(
            embryo,
            KittenEmbryoResult,
        )

        self.assertIsInstance(
            paternity.selection,
            KittenFatherSelectedEvent,
        )

        self.assertIsInstance(
            embryo.event,
            KittenEmbryoCreatedEvent,
        )

        self.assertFalse(
            hasattr(
                embryo.event,
                "to_dict",
            )
        )

        self.assertIsInstance(
            embryo.viability,
            KittenGeneticViabilityResult,
        )

        self.assertIs(
            event.ovulation,
            self.resolver
            .ovulation_resolver
            .history[-1],
        )

        self.assertIs(
            paternity.selection,
            self.resolver
            .paternity_resolver
            .history[-1],
        )

        self.assertIs(
            embryo.event,
            self.resolver
            .embryo_resolver
            .history[-1],
        )

        self.assertIs(
            embryo.phenotype.profile,
            embryo.event.profile,
        )

        self.assertEqual(
            event.father_names,
            (
                "father",
            ),
        )

        self.assertEqual(
            event.embryos_attempted,
            1,
        )

        self.assertEqual(
            event.viable_embryo_count,
            1,
        )

        self.assertEqual(
            result.to_dict(),
            event.to_dict(),
        )

    def test_nested_domain_state_has_no_mapping_api(
        self
    ):
        self._start_pregnancy()

        event = (
            self.resolver
            .history[-1]
        )

        paternity = (
            event
            .paternity_results[0]
        )

        embryo = (
            event
            .embryo_results[0]
        )

        objects = (
            event,
            event.ovulation,
            paternity,
            paternity.selection,
            embryo,
            embryo.event,
            embryo.viability,
            embryo.phenotype,
            embryo.phenotype.profile,
        )

        self.assertFalse(
            hasattr(
                embryo,
                "to_dict",
            )
        )

        self.assertFalse(
            hasattr(
                event.ovulation,
                "to_dict",
            )
        )

        for obj in objects:
            for mapping_method in (
                "get",
                "keys",
                "items",
                "values",
            ):
                self.assertFalse(
                    hasattr(
                        obj,
                        mapping_method,
                    )
                )

            with self.assertRaises(
                TypeError
            ):
                _ = obj["name"]

    def test_boundary_containers_are_detached(
        self
    ):
        result = (
            self._start_pregnancy()
        )

        event = (
            self.resolver
            .history[-1]
        )

        boundary = (
            result.to_dict()
        )

        boundary[
            "father_names"
        ].append(
            "changed"
        )

        boundary[
            "ovulation"
        ][
            "ovulation_induced"
        ] = False

        boundary[
            "paternity_results"
        ][0][
            "selection"
        ][
            "weighted_candidate_names"
        ].append(
            "changed"
        )

        boundary[
            "embryo_results"
        ][0][
            "viability"
        ][
            "special_traits"
        ].append(
            "changed"
        )

        boundary[
            "embryo_results"
        ][0][
            "phenotype"
        ][
            "profile"
        ][
            "color"
        ] = "changed"

        boundary[
            "embryo_results"
        ][0][
            "event"
        ][
            "profile"
        ][
            "color"
        ] = "changed"

        self.assertEqual(
            event.father_names,
            (
                "father",
            ),
        )

        self.assertTrue(
            event.ovulation.ovulation_induced
        )

        self.assertNotIn(
            "changed",
            event
            .paternity_results[0]
            .selection
            .weighted_candidate_names,
        )

        self.assertNotIn(
            "changed",
            event
            .embryo_results[0]
            .viability
            .special_traits,
        )

        self.assertNotEqual(
            event
            .embryo_results[0]
            .phenotype
            .profile
            .color,
            "changed",
        )

    def test_quantum_audit_is_detached_boundary(
        self
    ):
        self._start_pregnancy()

        event = (
            self.resolver
            .history[-1]
        )

        audit = (
            self.universe
            .quantum_events[-1]
        )

        self.assertIsInstance(
            audit,
            dict,
        )

        audit[
            "father_names"
        ].append(
            "changed"
        )

        audit[
            "paternity_results"
        ][0][
            "selection"
        ][
            "weighted_candidate_names"
        ].append(
            "changed"
        )

        self.assertEqual(
            event.father_names,
            (
                "father",
            ),
        )

        self.assertNotIn(
            "changed",
            event
            .paternity_results[0]
            .selection
            .weighted_candidate_names,
        )

    def test_nested_paternity_rejects_mapping(
        self
    ):
        with self.assertRaises(
            TypeError
        ):
            CatPregnancyPaternityResult(
                embryo_id="embryo_0001",
                selection={
                    "father": "father",
                },
            )


if __name__ == "__main__":
    unittest.main()
