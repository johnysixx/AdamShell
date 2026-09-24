import unittest

from universe.universe import Universe
from cats import Cats
from cats.cat_birth_objects import (
    CatBirthProfile,
)
from cats.genotype import CatGenotype
from cats.kitten_embryo_resolver import (
    KittenEmbryoCreatedEvent,
    KittenEmbryoResolver,
    KittenGeneticViabilitySnapshot,
    NonviableKittenEmbryoReplacedByCronenbergEvent,
)


class FirstChoiceRng:

    def choice(
        self,
        values,
    ):
        return list(values)[0]

    def randint(
        self,
        minimum,
        maximum,
    ):
        return minimum


class KittenEmbryoHistoryObjectStateTests(
    unittest.TestCase
):

    def setUp(self):
        self.universe = Universe()

        self.cats = Cats(
            self.universe
        )

        self.mother = self.cats.create_cat(
            name="mother_event",
            color="black",
            fur_length="short",
            sex="female",
        )

        self.father = self.cats.create_cat(
            name="father_event",
            color="black",
            fur_length="short",
            sex="male",
        )

        self.resolver = (
            KittenEmbryoResolver(
                self.universe
            )
        )

    def test_viable_history_uses_objects(
        self
    ):
        result = (
            self.resolver.create_embryo(
                mother=self.mother,
                father=self.father,
                rng=FirstChoiceRng(),
            )
        )

        event = (
            self.resolver
            .history[-1]
        )

        self.assertIsInstance(
            event,
            KittenEmbryoCreatedEvent,
        )

        self.assertIsInstance(
            event.profile,
            CatBirthProfile,
        )

        self.assertEqual(
            event.profile.sex,
            result[
                "event"
            ][
                "profile"
            ][
                "sex"
            ],
        )

        for mapping_method in (
            "get",
            "keys",
            "items",
            "values",
        ):
            self.assertFalse(
                hasattr(
                    event,
                    mapping_method,
                )
            )

        with self.assertRaises(TypeError):
            _ = event["profile"]

        result[
            "event"
        ][
            "profile"
        ][
            "sex"
        ] = "changed"

        self.assertNotEqual(
            event.profile.sex,
            "changed",
        )

    def test_nonviable_history_uses_object_state(
        self
    ):
        genotype = (
            CatGenotype.create_founder(
                sex="female",
                lethal_mutations=[
                    "embryonic_lethal",
                ],
            )
        )

        result = (
            self.resolver.create_embryo(
                mother=self.mother,
                father=self.father,
                rng=FirstChoiceRng(),
                genotype_override=genotype,
            )
        )

        event = (
            self.resolver
            .history[-1]
        )

        self.assertIsInstance(
            event,
            NonviableKittenEmbryoReplacedByCronenbergEvent,
        )

        self.assertIsInstance(
            event.viability,
            KittenGeneticViabilitySnapshot,
        )

        self.assertIs(
            event.genotype,
            genotype,
        )

        self.assertEqual(
            event.viability.status,
            "nonviable",
        )

        self.assertEqual(
            event.viability.details[
                "lethal_mutations"
            ],
            (
                "embryonic_lethal",
            ),
        )

        with self.assertRaises(TypeError):
            event.viability.details[
                "lethal_mutations"
            ] = ()

        result[
            "event"
        ][
            "viability"
        ][
            "details"
        ][
            "lethal_mutations"
        ][0] = "changed"

        self.assertEqual(
            event.viability.details[
                "lethal_mutations"
            ],
            (
                "embryonic_lethal",
            ),
        )

        self.assertEqual(
            self.universe
            .quantum_events[-1]
            ["viability"]
            ["details"]
            ["lethal_mutations"],
            [
                "embryonic_lethal",
            ],
        )

    def test_history_rejects_mapping_event(
        self
    ):
        with self.assertRaises(TypeError):
            self.resolver.record_event(
                {
                    "name": (
                        "kitten_embryo_created"
                    ),
                }
            )


if __name__ == "__main__":
    unittest.main()
