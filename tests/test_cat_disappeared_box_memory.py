import unittest

from universe.universe import Universe
from cats.cats import Cats
from cats.cat_mind import CatMind
from cats.cat_perception import CatPerception


class CatDisappearedBoxMemoryTests(
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

        self.cat["position"] = {
            "x": 0.0,
            "y": 0.0,
            "z": 0.0
        }

        self.box = (
            self.universe
            .create_quantum_box()
        )

        self.box.current_layer = (
            "quantum_layer"
        )

        self.box.position = {
            "x": 3.0,
            "y": 0.0,
            "z": 0.0
        }

    def test_disappeared_box_memory_is_not_current_box_target(
        self
    ):
        box_id = self.box.id

        self.cat[
            "mind"
        ][
            "current_intention"
        ] = {
            "type": "explore_box",
            "target": box_id,
            "score": 1.0,
            "reasons": [
                "test"
            ]
        }

        result = (
            self.cats
            .execute_cat_intention(
                self.cat
            )
        )

        for _ in range(10):
            if result[
                "name"
            ] == "cat_explored_quantum_box":
                break

            result = (
                self.cats
                .execute_cat_intention(
                    self.cat
                )
            )

        self.assertEqual(
            result["name"],
            "cat_explored_quantum_box"
        )

        # Historick? vzpom?nka existuje.
        memories = (
            self.cat[
                "memory"
            ].recall(
                event_type=(
                    "quantum_box_observed"
                )
            )
        )

        self.assertTrue(
            any(
                box_id
                in memory.get(
                    "participants",
                    []
                )
                for memory
                in memories
            )
        )

        # Box mezit?m zanikne.
        self.universe.quantum_boxes.remove(
            self.box
        )

        observations = CatPerception(
            self.cats
        ).observe(
            self.cat
        )

        # V aktu?ln? realit? u? nen?.
        self.assertNotIn(
            box_id,
            observations[
                "visible_boxes"
            ]
        )

        self.assertNotIn(
            box_id,
            observations[
                "unexplored_boxes"
            ]
        )

        # A CatMind z pam?ti nevykouzl?
        # neexistuj?c? krabici zp?tky.
        candidates = CatMind.consider(
            cat=self.cat,
            observations=observations
        )

        stale_box_targets = [
            candidate
            for candidate in candidates
            if (
                candidate.get(
                    "type"
                ) == "explore_box"
                and (
                    candidate.get(
                        "target"
                    ) == box_id
                    or (
                        isinstance(
                            candidate.get(
                                "target"
                            ),
                            dict
                        )
                        and (
                            candidate[
                                "target"
                            ].get(
                                "id"
                            ) == box_id
                            or candidate[
                                "target"
                            ].get(
                                "box_id"
                            ) == box_id
                        )
                    )
                )
            )
        ]

        self.assertEqual(
            stale_box_targets,
            []
        )

        # Ale historick? vzpom?nka nezmizela.
        memories_after = (
            self.cat[
                "memory"
            ].recall(
                event_type=(
                    "quantum_box_observed"
                )
            )
        )

        self.assertTrue(
            any(
                box_id
                in memory.get(
                    "participants",
                    []
                )
                for memory
                in memories_after
            )
        )


if __name__ == "__main__":
    unittest.main()
