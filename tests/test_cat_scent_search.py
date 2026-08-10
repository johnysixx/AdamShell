import unittest

from universe.universe import Universe
from cats.cats import Cats
from cats.cat_mind import CatMind
from cats.cat_perception import CatPerception


class CatScentSearchTests(
    unittest.TestCase
):

    def setUp(self):
        self.universe = Universe()
        self.universe.enable_quantum_layer()

        self.cats = Cats(
            self.universe
        )

        self.cat = self.cats.create_cat(
            name="tracker",
            color="black",
            fur_length="short"
        )

        self.cat[
            "current_layer"
        ] = "quantum_layer"

        self.cat["position"] = {
            "x": 3.0,
            "y": 0.0,
            "z": 0.0
        }

        traits = self.cat[
            "personality"
        ][
            "traits"
        ]

        traits["curiosity"] = 1.0
        traits["courage"] = 1.0

        self.cat[
            "known_scent_follow"
        ] = {
            "active": False,
            "arrived": True,
            "identity": "cat:pazuzu",
            "source_id": "latest_trace",
            "destination": {
                "x": 3.0,
                "y": 0.0,
                "z": 0.0
            },
            "trail_direction": {
                "inferred": True,
                "unit_vector": {
                    "x": 1.0,
                    "y": 0.0,
                    "z": 0.0
                },
                "confidence": 0.8
            }
        }

    def observations(self):
        return CatPerception(
            self.cats
        ).observe(
            self.cat
        )

    def test_mind_considers_search_when_scent_is_lost(
        self
    ):
        candidates = CatMind.consider(
            cat=self.cat,
            observations=self.observations()
        )

        search = [
            candidate
            for candidate in candidates
            if candidate[
                "type"
            ] == "search_for_scent"
        ]

        self.assertEqual(
            len(search),
            1
        )

        self.assertEqual(
            search[0][
                "target"
            ][
                "identity"
            ],
            "cat:pazuzu"
        )

    def test_search_is_physical_and_limited(
        self
    ):
        candidates = CatMind.consider(
            cat=self.cat,
            observations=self.observations()
        )

        intention = next(
            candidate
            for candidate in candidates
            if candidate[
                "type"
            ] == "search_for_scent"
        )

        self.cat[
            "mind"
        ][
            "current_intention"
        ] = intention

        first = (
            self.cats
            .execute_cat_intention(
                self.cat
            )
        )

        self.assertEqual(
            first["name"],
            "cat_searching_for_scent"
        )

        self.assertEqual(
            self.cat["position"],
            {
                "x": 3.0,
                "y": 0.0,
                "z": 0.0
            }
        )

        result = first

        for _ in range(10):
            result = (
                self.cats
                .execute_cat_intention(
                    self.cat
                )
            )

            if result["name"] == (
                "cat_completed_scent_search_step"
            ):
                break

        self.assertEqual(
            result["name"],
            "cat_completed_scent_search_step"
        )

        self.assertGreater(
            self.cat[
                "position"
            ][
                "x"
            ],
            3.0
        )

        self.assertEqual(
            self.cat[
                "scent_search"
            ][
                "attempts"
            ],
            1
        )

        self.assertIsNone(
            self.cat[
                "mind"
            ][
                "current_intention"
            ]
        )


if __name__ == "__main__":
    unittest.main()