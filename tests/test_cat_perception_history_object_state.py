import unittest

from universe.universe import Universe
from cats.cats import Cats
from core.entity.components import (
    SpatialVector3,
)
from cats.cat_perception import (
    CatEnvironmentObservedEvent,
)
from cats.cat_perception_state import (
    CatPerceptionState,
)


class CatPerceptionHistoryObjectStateTests(
    unittest.TestCase
):

    def setUp(self):
        self.universe = Universe()

        self.universe.enable_quantum_layer()

        self.cats = Cats(
            self.universe
        )

        self.cat = self.cats.create_cat(
            name="perception_history_cat",
            color="black",
            fur_length="short",
        )

        self.cat.position = (
            SpatialVector3.zero()
        )

    def test_history_uses_object_state(
        self
    ):
        result = (
            self.cats.observe_cat(
                self.cat
            )
        )

        event = (
            self.cats
            .perception
            .history[-1]
        )

        self.assertIsInstance(
            event,
            CatEnvironmentObservedEvent,
        )

        self.assertIsInstance(
            event.observations,
            CatPerceptionState,
        )

        self.assertEqual(
            event.cat,
            self.cat.name,
        )

        self.assertEqual(
            event.observations.cat,
            result.cat,
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
            _ = event["cat"]

    def test_returned_state_is_detached_from_history(
        self
    ):
        result = (
            self.cats.observe_cat(
                self.cat
            )
        )

        event = (
            self.cats
            .perception
            .history[-1]
        )

        result.cat = "changed"

        result.nearby_cats.append(
            "changed"
        )

        self.assertEqual(
            event.observations.cat,
            self.cat.name,
        )

        self.assertNotIn(
            "changed",
            event.observations.nearby_cats,
        )

    def test_audit_histories_keep_detached_snapshot(
        self
    ):
        self.cats.observe_cat(
            self.cat
        )

        event = (
            self.cats
            .perception
            .history[-1]
        )

        mind_audit = (
            self.cat
            .mind
            .observation_history[-1]
        )

        quantum_audit = (
            self.universe
            .quantum_events[-1]
        )

        self.assertIsInstance(
            mind_audit,
            dict,
        )

        self.assertIsInstance(
            quantum_audit,
            dict,
        )

        self.assertIsInstance(
            mind_audit[
                "observations"
            ],
            CatPerceptionState,
        )

        mind_audit[
            "observations"
        ].cat = "changed"

        quantum_audit[
            "observations"
        ].cat = "changed_again"

        self.assertEqual(
            event.observations.cat,
            self.cat.name,
        )

    def test_history_rejects_mapping_event(
        self
    ):
        with self.assertRaises(TypeError):
            (
                self.cats
                .perception
                .record_event(
                    {
                        "name": (
                            "cat_environment_observed"
                        ),
                    }
                )
            )


if __name__ == "__main__":
    unittest.main()
