from core.entity.social_entity import SocialEntity
import unittest

from gods.gods import Gods
from meeting_place.meeting_place import MeetingPlace
from multiverse import UniverseRegistry
from quantum.director import QuantumDirector
from quantum.director_state import (
    QuantumDirectorArrivedAtBarEvent,
    QuantumDirectorMaterialSample,
)
from universe.universe import Universe


class DirectorBarArrivalTests(
    unittest.TestCase
):

    def test_director_arrives_at_bar_with_liquid_hydrocarbon_sample_and_meets_serpent(
        self
    ):
        universe = Universe()

        universe.universe_registry = (
            UniverseRegistry()
        )

        meeting_place = MeetingPlace(
            universe
        )

        universe.meeting_place = (
            meeting_place
        )

        gods = Gods(
            universe
        )

        god = gods.create_god(
            name="god",
            role="creator_entity",
        )

        director = QuantumDirector(
            universe=universe,
            god=god,
            gods=gods,
        )

        serpent = (
            SocialEntity.from_mapping(
                {
                    "name": "serpent",
                    "type": "idea_entity",
                    "role":
                        "primordial_serpent",
                }
            )
        )

        meeting_place.entities.append(
            serpent
        )

        sample = (
            QuantumDirectorMaterialSample(
                material=(
                    "liquid_hydrocarbons"
                ),
                amount=3.0,
            )
        )

        result = director.arrive_at_bar(
            meeting_place=meeting_place,
            sample=sample,
        )

        self.assertIn(
            director,
            meeting_place.entities,
        )

        self.assertIsInstance(
            result,
            QuantumDirectorArrivedAtBarEvent,
        )

        self.assertIs(
            result.sample,
            sample,
        )

        self.assertEqual(
            result.sample.material,
            "liquid_hydrocarbons",
        )

        self.assertEqual(
            result.sample.amount,
            3.0,
        )

        self.assertIs(
            result.met,
            serpent,
        )

        self.assertTrue(
            result.serpent_present
        )

        self.assertEqual(
            result.event,
            "director_arrived_at_bar",
        )

        self.assertIs(
            director.research_book[-1],
            result,
        )

        for value in (
            sample,
            result,
        ):
            for mapping_method in (
                "get",
                "keys",
                "items",
                "values",
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
            _ = result[
                "sample"
            ]

    def test_director_rejects_mapping_sample(
        self
    ):
        universe = Universe()

        universe.universe_registry = (
            UniverseRegistry()
        )

        meeting_place = MeetingPlace(
            universe
        )

        gods = Gods(
            universe
        )

        god = gods.create_god(
            name="god",
            role="creator_entity",
        )

        director = QuantumDirector(
            universe=universe,
            god=god,
            gods=gods,
        )

        with self.assertRaises(
            TypeError
        ):
            director.arrive_at_bar(
                meeting_place=meeting_place,
                sample={
                    "material":
                        "liquid_hydrocarbons",
                    "amount":
                        3.0,
                },
            )


if __name__ == "__main__":
    unittest.main()
