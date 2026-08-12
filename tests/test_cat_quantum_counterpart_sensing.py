import unittest

from universe.universe import Universe
from cats.cats import Cats
from cats.cat_mind import CatMind
from cats.cat_perception import CatPerception


class CatQuantumCounterpartSensingTests(
    unittest.TestCase
):

    def setUp(self):
        self.universe = Universe()
        self.universe.enable_quantum_layer()

        self.cats = Cats(
            self.universe
        )

        self.cat = self.cats.create_cat(
            name="observer",
            color="black",
            fur_length="short"
        )

        self.cat[
            "current_layer"
        ] = "quantum_layer"

        self.source = (
            self.universe
            .create_quantum_box()
        )

        self.target = (
            self.universe
            .create_quantum_box()
        )

        self.source.current_layer = (
            "quantum_layer"
        )

        self.target.current_layer = (
            "meeting_place"
        )

        self.source.position = {
            "x": 2.0,
            "y": 0.0,
            "z": 0.0
        }

        self.target.position = {
            "x": 9.0,
            "y": 4.0,
            "z": 0.0
        }

        self.source.pair_with(
            self.target
        )

        self.cat["position"] = {
            "x": 2.0,
            "y": 0.0,
            "z": 0.0
        }

        # Box u? ko?ka skute?n? zn?
        # jako d??ve prozkouman?.
        self.cat[
            "memory"
        ].remember(
            event_type=(
                "quantum_box_observed"
            ),
            universe_tick=0,
            location=(
                "quantum_layer"
            ),
            participants=[
                self.source.id
            ],
            details={
                "box_id": self.source.id
            }
        )

    def observations(self):
        return CatPerception(
            self.cats
        ).observe(
            self.cat
        )

    def test_cat_can_choose_to_sense_counterpart(
        self
    ):
        observations = self.observations()

        candidates = CatMind.consider(
            cat=self.cat,
            observations=observations
        )

        resonance = [
            candidate
            for candidate in candidates
            if candidate[
                "type"
            ] == (
                "sense_quantum_counterpart"
            )
        ]

        self.assertEqual(
            len(resonance),
            1
        )

        self.assertEqual(
            resonance[0][
                "target"
            ][
                "box_id"
            ],
            self.source.id
        )

    def test_sensing_reveals_current_counterpart_location(
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
            ] == (
                "sense_quantum_counterpart"
            )
        )

        self.cat[
            "mind"
        ][
            "current_intention"
        ] = intention

        result = (
            self.cats
            .execute_cat_intention(
                self.cat
            )
        )

        self.assertEqual(
            result["name"],
            "cat_sensed_quantum_counterpart"
        )

        observation = result[
            "observation"
        ]

        self.assertEqual(
            observation[
                "counterpart_box_id"
            ],
            self.target.id
        )

        self.assertEqual(
            observation[
                "counterpart_layer"
            ],
            "meeting_place"
        )

        self.assertEqual(
            observation[
                "counterpart_position"
            ],
            self.target.position
        )

        self.assertTrue(
            observation[
                "temporary"
            ]
        )

        self.assertTrue(
            observation[
                "pair_currently_valid"
            ]
        )

    def test_counterpart_observation_disappears_with_pair(
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
            ] == (
                "sense_quantum_counterpart"
            )
        )

        self.cat[
            "mind"
        ][
            "current_intention"
        ] = intention

        result = (
            self.cats
            .execute_cat_intention(
                self.cat
            )
        )

        self.assertTrue(
            result[
                "observation"
            ][
                "pair_currently_valid"
            ]
        )

        before = self.observations()

        self.assertIsNotNone(
            before[
                "quantum_counterpart_observation"
            ]
        )

        # Druh? p?lka p?ru zmiz?.
        self.universe.quantum_boxes.remove(
            self.target
        )

        after = self.observations()

        self.assertIsNone(
            after[
                "quantum_counterpart_observation"
            ]
        )

        self.assertNotIn(
            "current_quantum_counterpart_observation",
            self.cat
        )


if __name__ == "__main__":
    unittest.main()
