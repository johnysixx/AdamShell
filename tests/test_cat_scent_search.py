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


    def test_search_stops_when_target_scent_is_reacquired(
        self
    ):
        pazuzu = self.cats.create_cat(
            name="pazuzu",
            color="black",
            fur_length="short"
        )

        pazuzu[
            "current_layer"
        ] = "quantum_layer"

        pazuzu["position"] = {
            "x": 17.5,
            "y": 0.0,
            "z": 0.0
        }

        self.universe.entities.append(
            self.cat
        )

        self.universe.entities.append(
            pazuzu
        )

        self.cats.learn_cat_aroma(
            observer=self.cat,
            observed_cat=pazuzu
        )

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

        started = (
            self.cats
            .execute_cat_intention(
                self.cat
            )
        )

        self.assertEqual(
            started["name"],
            "cat_searching_for_scent"
        )

        reacquired = (
            self.cats
            .execute_cat_intention(
                self.cat
            )
        )

        self.assertEqual(
            reacquired["name"],
            (
                "cat_reacquired_scent_"
                "during_search"
            )
        )

        self.assertEqual(
            reacquired["identity"],
            "cat:pazuzu"
        )

        self.assertTrue(
            reacquired[
                "search_interrupted"
            ]
        )

        self.assertFalse(
            self.cat[
                "scent_search"
            ][
                "active"
            ]
        )

        self.assertTrue(
            self.cat[
                "scent_search"
            ][
                "reacquired"
            ]
        )

        self.assertIsNone(
            self.cat[
                "mind"
            ][
                "current_intention"
            ]
        )

        self.assertNotIn(
            "active_route_id",
            self.cat
        )

        route = (
            self.universe
            .quantum_space
            .find_cat_route(
                self.cat["name"]
            )
        )

        self.assertIsNone(
            route
        )

        memories = self.cat[
            "knowledge"
        ][
            "known_scent_places"
        ]

        self.assertTrue(
            any(
                memory.get(
                    "identity"
                ) == "cat:pazuzu"
                for memory
                in memories
            )
        )


    def test_search_stops_after_max_attempts(
        self
    ):
        self.cat[
            "scent_search"
        ] = {
            "active": False,
            "identity": "cat:pazuzu",
            "layer": "quantum_layer",
            "attempts": 3,
            "max_attempts": 3,
            "arrived": True
        }

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
            search,
            []
        )

        self.assertTrue(
            self.cat[
                "known_scent_follow"
            ][
                "arrived"
            ]
        )

        self.assertEqual(
            self.cat[
                "scent_search"
            ][
                "attempts"
            ],
            3
        )


    def test_exhausted_search_returns_cat_to_normal_decision_candidates(
        self
    ):
        self.cat[
            "scent_search"
        ] = {
            "active": False,
            "identity": "cat:pazuzu",
            "layer": "quantum_layer",
            "attempts": 3,
            "max_attempts": 3,
            "arrived": True
        }

        self.cat[
            "mind"
        ][
            "current_intention"
        ] = None

        candidates = CatMind.consider(
            cat=self.cat,
            observations=self.observations()
        )

        self.assertTrue(
            candidates
        )

        types = {
            candidate["type"]
            for candidate in candidates
        }

        self.assertNotIn(
            "search_for_scent",
            types
        )

        self.assertIn(
            "rest",
            types
        )

        decision = CatMind.decide(
            cat=self.cat,
            observations=self.observations(),
            quantum_roll=None
        )

        self.assertTrue(
            decision[
                "selected"
            ]
        )

        self.assertNotEqual(
            decision[
                "intention"
            ],
            "search_for_scent"
        )

        self.assertIsNotNone(
            self.cat[
                "mind"
            ][
                "current_intention"
            ]
        )


if __name__ == "__main__":
    unittest.main()