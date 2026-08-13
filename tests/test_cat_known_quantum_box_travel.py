import unittest

from universe.universe import Universe
from cats.cats import Cats
from cats.cat_mind import CatMind
from cats.cat_perception import CatPerception


class CatKnownQuantumBoxTravelTests(
    unittest.TestCase
):

    def setUp(self):
        self.universe = Universe()
        self.universe.enable_quantum_layer()

        self.cats = Cats(
            self.universe
        )

        self.cat = self.cats.create_cat(
            name="traveler",
            color="black",
            fur_length="short"
        )

        self.cat["current_layer"] = (
            "quantum_layer"
        )

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

        self.cat["position"] = dict(
            self.source.position
        )

        self.cat[
            "memory"
        ].remember(
            event_type=(
                "quantum_box_observed"
            ),
            universe_tick=0,
            location="quantum_layer",
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

    def sense_counterpart(self):
        candidates = CatMind.consider(
            cat=self.cat,
            observations=self.observations()
        )

        intention = next(
            candidate
            for candidate in candidates
            if candidate["type"]
            == "sense_quantum_counterpart"
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
            result["executed"]
        )

    def test_current_observation_creates_travel_intention(
        self
    ):
        self.sense_counterpart()

        candidates = CatMind.consider(
            cat=self.cat,
            observations=self.observations()
        )

        travel = next(
            candidate
            for candidate in candidates
            if candidate["type"]
            == "travel_through_known_quantum_box"
        )

        self.assertEqual(
            travel[
                "target"
            ][
                "source_box_id"
            ],
            self.source.id
        )

        self.assertEqual(
            travel[
                "target"
            ][
                "counterpart_box_id"
            ],
            self.target.id
        )

    def test_travel_intention_transfers_cat(
        self
    ):
        self.sense_counterpart()

        candidates = CatMind.consider(
            cat=self.cat,
            observations=self.observations()
        )

        travel = next(
            candidate
            for candidate in candidates
            if candidate["type"]
            == "travel_through_known_quantum_box"
        )

        self.cat[
            "mind"
        ][
            "current_intention"
        ] = travel

        result = (
            self.cats
            .execute_cat_intention(
                self.cat
            )
        )

        self.assertTrue(
            result["executed"]
        )

        self.assertEqual(
            result["name"],
            "cat_traveled_through_known_quantum_box"
        )

        self.assertEqual(
            self.cat[
                "current_layer"
            ],
            self.target.current_layer
        )

        self.assertEqual(
            self.cat[
                "position"
            ],
            self.target.position
        )

    def test_stale_observation_cannot_teleport_from_distance(
        self
    ):
        self.sense_counterpart()

        candidates = CatMind.consider(
            cat=self.cat,
            observations=self.observations()
        )

        travel = next(
            candidate
            for candidate in candidates
            if candidate["type"]
            == "travel_through_known_quantum_box"
        )

        self.cat["position"] = {
            "x": 100.0,
            "y": 100.0,
            "z": 0.0
        }

        self.cat[
            "mind"
        ][
            "current_intention"
        ] = travel

        result = (
            self.cats
            .execute_cat_intention(
                self.cat
            )
        )

        self.assertFalse(
            result["executed"]
        )

        self.assertEqual(
            result["reason"],
            "cat_not_at_source_box"
        )

        self.assertEqual(
            self.cat[
                "current_layer"
            ],
            "quantum_layer"
        )


    def test_successful_travel_is_remembered_as_route(
        self
    ):
        self.sense_counterpart()

        candidates = CatMind.consider(
            cat=self.cat,
            observations=self.observations()
        )

        travel = next(
            candidate
            for candidate in candidates
            if candidate["type"]
            == "travel_through_known_quantum_box"
        )

        self.cat[
            "mind"
        ][
            "current_intention"
        ] = travel

        result = (
            self.cats
            .execute_cat_intention(
                self.cat
            )
        )

        self.assertTrue(
            result["executed"]
        )

        memories = self.cat[
            "memory"
        ].recall(
            event_type=(
                "quantum_box_layer_transfer"
            )
        )

        self.assertTrue(
            memories
        )

        memory = memories[-1]

        self.assertEqual(
            memory[
                "participants"
            ],
            [
                self.source.id,
                self.target.id
            ]
        )

        self.assertEqual(
            memory[
                "details"
            ][
                "source_layer"
            ],
            "quantum_layer"
        )

        self.assertEqual(
            memory[
                "details"
            ][
                "target_layer"
            ],
            "meeting_place"
        )

        self.assertTrue(
            memory[
                "details"
            ][
                "target_box_consumed"
            ]
        )

if __name__ == "__main__":
    unittest.main()

