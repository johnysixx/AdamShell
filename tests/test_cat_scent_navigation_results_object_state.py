import unittest

from cats.cat_intention_state import (
    CatIntentionCandidate,
    CatKnownScentTarget,
    CatScentSearchTarget,
)
from cats.cat_scent_direction_state import (
    CatScentTrailDirection,
)
from cats.cat_scent_navigation_result_state import (
    CatKnownScentFollowFailedResult,
    CatKnownScentFollowingEvent,
    CatKnownScentReachedEvent,
    CatScentSearchFailedResult,
    CatScentSearchingEvent,
)
from cats.cats import Cats
from core.entity.components import (
    SpatialVector3,
)
from universe.universe import Universe


class CatScentNavigationResultsObjectStateTests(
    unittest.TestCase
):

    def setUp(self):
        self.universe = Universe()

        self.universe.enable_quantum_layer()

        self.cats = Cats(
            self.universe
        )

        self.cat = (
            self.cats.create_cat(
                name="scent_result_cat",
                color="black",
                fur_length="short",
            )
        )

        self.cat.current_layer = (
            "quantum_layer"
        )

        self.cat.position = (
            SpatialVector3.zero()
        )

    def assert_object_only(
        self,
        value,
    ):
        for mapping_method in (
            "get",
            "keys",
            "items",
            "values",
            "to_dict",
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
            _ = value[
                "name"
            ]

    def test_search_failure_is_object(
        self
    ):
        self.cat.mind.current_intention = (
            CatIntentionCandidate(
                type="search_for_scent",
                target="invalid",
                score=1.0,
                reasons=["test"],
            )
        )

        result = (
            self.cats
            .execute_cat_intention(
                self.cat
            )
        )

        self.assertIsInstance(
            result,
            CatScentSearchFailedResult,
        )

        self.assertFalse(
            result.executed
        )

        self.assertEqual(
            result.reason,
            "invalid_search_target",
        )

        self.assert_object_only(
            result
        )

    def test_search_started_event_uses_spatial_objects(
        self
    ):
        direction = (
            CatScentTrailDirection(
                inferred=True,
                unit_vector=(
                    SpatialVector3(
                        x=1.0,
                        y=0.0,
                        z=0.0,
                    )
                ),
                confidence=0.8,
            )
        )

        self.cat.mind.current_intention = (
            CatIntentionCandidate(
                type="search_for_scent",
                target=CatScentSearchTarget(
                    identity="cat:pazuzu",
                    layer="quantum_layer",
                    from_position=
                        self.cat.position,
                    trail_direction=
                        direction,
                    attempt=1,
                    max_attempts=3,
                    search_distance=2.0,
                ),
                score=1.0,
                reasons=["test"],
            )
        )

        result = (
            self.cats
            .execute_cat_intention(
                self.cat
            )
        )

        self.assertIsInstance(
            result,
            CatScentSearchingEvent,
        )

        self.assertIsInstance(
            result.start_position,
            SpatialVector3,
        )

        self.assertIsInstance(
            result.destination,
            SpatialVector3,
        )

        self.assertEqual(
            result.destination,
            SpatialVector3(
                x=2.0,
                y=0.0,
                z=0.0,
            ),
        )

        self.assert_object_only(
            result
        )

        active = (
            self.cat
            .mind
            .active_body_execution
        )

        self.assertIsInstance(
            active,
            CatScentSearchingEvent,
        )

        self.assertEqual(
            active,
            result,
        )

        self.assertIsNot(
            active,
            result,
        )

        stored = (
            self.cats
            .intention_executor
            .history[-1]
        )

        self.assertIsInstance(
            stored,
            CatScentSearchingEvent,
        )

        self.assertEqual(
            stored,
            result,
        )

        self.assertIsNot(
            stored,
            result,
        )

    def test_known_scent_failure_is_object(
        self
    ):
        self.cat.mind.current_intention = (
            CatIntentionCandidate(
                type="follow_known_scent",
                target="invalid",
                score=1.0,
                reasons=["test"],
            )
        )

        result = (
            self.cats
            .execute_cat_intention(
                self.cat
            )
        )

        self.assertIsInstance(
            result,
            CatKnownScentFollowFailedResult,
        )

        self.assertFalse(
            result.executed
        )

        self.assert_object_only(
            result
        )

    def test_known_scent_follow_started_event_is_object(
        self
    ):
        destination = (
            SpatialVector3(
                x=3.0,
                y=0.0,
                z=0.0,
            )
        )

        self.cat.mind.current_intention = (
            CatIntentionCandidate(
                type="follow_known_scent",
                target=CatKnownScentTarget(
                    identity="cat:pazuzu",
                    layer="quantum_layer",
                    position=destination,
                    source_id="trace_latest",
                    trail_direction=(
                        CatScentTrailDirection(
                            inferred=True,
                            unit_vector=(
                                SpatialVector3(
                                    x=1.0,
                                    y=0.0,
                                    z=0.0,
                                )
                            ),
                            confidence=0.8,
                        )
                    ),
                ),
                score=1.0,
                reasons=["test"],
            )
        )

        result = (
            self.cats
            .execute_cat_intention(
                self.cat
            )
        )

        self.assertIsInstance(
            result,
            CatKnownScentFollowingEvent,
        )

        self.assertEqual(
            result.destination,
            destination,
        )

        self.assert_object_only(
            result
        )

    def test_known_scent_reached_event_is_object(
        self
    ):
        destination = (
            SpatialVector3(
                x=3.0,
                y=0.0,
                z=0.0,
            )
        )

        self.cat.position = (
            destination
        )

        self.cat.mind.current_intention = (
            CatIntentionCandidate(
                type="follow_known_scent",
                target=CatKnownScentTarget(
                    identity="cat:pazuzu",
                    layer="quantum_layer",
                    position=destination,
                    source_id="trace_latest",
                    trail_direction=(
                        CatScentTrailDirection(
                            inferred=True,
                            unit_vector=(
                                SpatialVector3(
                                    x=1.0,
                                    y=0.0,
                                    z=0.0,
                                )
                            ),
                            confidence=0.8,
                        )
                    ),
                ),
                score=1.0,
                reasons=["test"],
            )
        )

        result = (
            self.cats
            .execute_cat_intention(
                self.cat
            )
        )

        self.assertIsInstance(
            result,
            CatKnownScentReachedEvent,
        )

        self.assertTrue(
            result.arrived
        )

        self.assertEqual(
            result.destination,
            destination,
        )

        self.assertIsNone(
            self.cat
            .mind
            .current_intention
        )

        self.assert_object_only(
            result
        )


if __name__ == "__main__":
    unittest.main()
