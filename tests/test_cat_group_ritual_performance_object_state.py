import unittest

from cats.cat_cultural_tradition_state import (
    CatCulturalTraditionState,
)
from cats.cat_group_ritual_performance_state import (
    CatGroupRitualPerformedEvent,
    CatGroupRitualPerformanceDeniedResult,
)
from cats.cat_group_ritual_system import (
    CatGroupRitualSystem,
)
from cats.cat_group_system import (
    CatGroupSystem,
)
from cats.cats import Cats
from universe.universe import Universe


class CatGroupRitualPerformanceObjectStateTests(
    unittest.TestCase
):

    def setUp(self):
        self.universe = Universe()

        self.cats = Cats(
            self.universe
        )

        self.first = (
            self.cats.create_cat(
                name="first",
                color="black",
                fur_length="short",
            )
        )

        self.second = (
            self.cats.create_cat(
                name="second",
                color="white",
                fur_length="short",
            )
        )

        self.outsider = (
            self.cats.create_cat(
                name="outsider",
                color="gray",
                fur_length="short",
            )
        )

        self.groups = (
            CatGroupSystem(
                self.cats
            )
        )

        self.group_id = (
            self.groups.create_group(
                self.first,
                name="ritual_group",
            ).group_id
        )

        self.groups.add_member(
            self.group_id,
            self.second,
            self.cats.cats,
        )

        self.rituals = (
            CatGroupRitualSystem(
                self.groups
            )
        )

    def define_ritual(
        self
    ):
        return (
            self.rituals.define(
                self.group_id,
                "evening_patrol",
                "territory",
            )
        )

    def assert_not_mapping(
        self,
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
                    result,
                    mapping_method,
                )
            )

        with self.assertRaises(
            TypeError
        ):
            _ = result[
                "performed"
            ]

    def test_unknown_ritual_returns_denied_object(
        self
    ):
        group = (
            self.groups.groups[
                self.group_id
            ]
        )

        history_before = len(
            group.history
        )

        result = (
            self.rituals.perform(
                self.group_id,
                "missing_ritual",
                [
                    self.first
                ],
            )
        )

        self.assertIsInstance(
            result,
            CatGroupRitualPerformanceDeniedResult,
        )

        self.assertFalse(
            result.performed
        )

        self.assertEqual(
            result.name,
            "cat_group_ritual_denied",
        )

        self.assertEqual(
            result.reason,
            "unknown_ritual",
        )

        self.assertFalse(
            hasattr(
                result,
                "to_dict",
            )
        )

        self.assertEqual(
            len(
                group.history
            ),
            history_before,
        )

        self.assert_not_mapping(
            result
        )

    def test_no_group_participants_returns_denied_object(
        self
    ):
        self.define_ritual()

        group = (
            self.groups.groups[
                self.group_id
            ]
        )

        ritual = (
            group.rituals[
                "evening_patrol"
            ]
        )

        result = (
            self.rituals.perform(
                self.group_id,
                "evening_patrol",
                [
                    self.outsider
                ],
            )
        )

        self.assertIsInstance(
            result,
            CatGroupRitualPerformanceDeniedResult,
        )

        self.assertFalse(
            result.performed
        )

        self.assertEqual(
            result.reason,
            "no_group_participants",
        )

        self.assertEqual(
            ritual.performances,
            0,
        )

        self.assertEqual(
            ritual.strength,
            0.0,
        )

        self.assertEqual(
            self.outsider.social_interactions,
            [],
        )

        self.assert_not_mapping(
            result
        )

    def test_perform_returns_typed_event(
        self
    ):
        self.define_ritual()

        result = (
            self.rituals.perform(
                self.group_id,
                "evening_patrol",
                [
                    self.first,
                    self.second,
                ],
            )
        )

        self.assertIsInstance(
            result,
            CatGroupRitualPerformedEvent,
        )

        self.assertTrue(
            result.performed
        )

        self.assertEqual(
            result.name,
            "cat_group_ritual_performed",
        )

        self.assertEqual(
            result.group_id,
            self.group_id,
        )

        self.assertEqual(
            result.ritual,
            "evening_patrol",
        )

        self.assertEqual(
            result.participants,
            (
                self.first.name,
                self.second.name,
            ),
        )

        self.assertIsInstance(
            result.participants,
            tuple,
        )

        self.assertAlmostEqual(
            result.strength,
            0.1,
        )

        self.assert_not_mapping(
            result
        )

    def test_performance_updates_ritual_domain_state(
        self
    ):
        self.define_ritual()

        self.rituals.perform(
            self.group_id,
            "evening_patrol",
            [
                self.first,
                self.second,
            ],
        )

        ritual = (
            self.groups.groups[
                self.group_id
            ].rituals[
                "evening_patrol"
            ]
        )

        self.assertEqual(
            ritual.performances,
            1,
        )

        self.assertAlmostEqual(
            ritual.strength,
            0.1,
        )

        self.assertEqual(
            ritual.last_participants,
            [
                self.first.name,
                self.second.name,
            ],
        )

    def test_performance_updates_typed_tradition_state(
        self
    ):
        self.define_ritual()

        self.rituals.perform(
            self.group_id,
            "evening_patrol",
            [
                self.first
            ],
        )

        tradition = (
            self.groups.groups[
                self.group_id
            ].culture.traditions[
                "evening_patrol"
            ]
        )

        self.assertIsInstance(
            tradition,
            CatCulturalTraditionState,
        )

        self.assertEqual(
            tradition.name,
            "evening_patrol",
        )

        self.assertEqual(
            tradition.category,
            "ritual",
        )

        self.assertEqual(
            tradition.occurrences,
            1,
        )

        self.assertAlmostEqual(
            tradition.strength,
            0.08,
        )

    def test_repeated_performance_reuses_tradition_object(
        self
    ):
        self.define_ritual()

        self.rituals.perform(
            self.group_id,
            "evening_patrol",
            [
                self.first
            ],
        )

        group = (
            self.groups.groups[
                self.group_id
            ]
        )

        stored = (
            group.culture.traditions[
                "evening_patrol"
            ]
        )

        result = (
            self.rituals.perform(
                self.group_id,
                "evening_patrol",
                [
                    self.second
                ],
            )
        )

        current = (
            group.culture.traditions[
                "evening_patrol"
            ]
        )

        self.assertIs(
            current,
            stored,
        )

        self.assertEqual(
            current.occurrences,
            2,
        )

        self.assertAlmostEqual(
            current.strength,
            0.16,
        )

        self.assertAlmostEqual(
            result.strength,
            0.2,
        )

    def test_outsider_is_excluded_from_successful_performance(
        self
    ):
        self.define_ritual()

        result = (
            self.rituals.perform(
                self.group_id,
                "evening_patrol",
                [
                    self.first,
                    self.outsider,
                ],
            )
        )

        self.assertEqual(
            result.participants,
            (
                self.first.name,
            ),
        )

        ritual = (
            self.groups.groups[
                self.group_id
            ].rituals[
                "evening_patrol"
            ]
        )

        self.assertEqual(
            ritual.last_participants,
            [
                self.first.name
            ],
        )

        self.assertEqual(
            self.outsider.social_interactions,
            [],
        )

    def test_history_is_serialized_detached_boundary(
        self
    ):
        self.define_ritual()

        group = (
            self.groups.groups[
                self.group_id
            ]
        )

        result = (
            self.rituals.perform(
                self.group_id,
                "evening_patrol",
                [
                    self.first,
                    self.second,
                ],
            )
        )

        stored = (
            group.history[
                -1
            ]
        )

        self.assertIsInstance(
            stored,
            dict,
        )

        self.assertIsNot(
            stored,
            result,
        )

        self.assertEqual(
            stored,
            result.to_dict(),
        )

        self.assertIsInstance(
            stored[
                "participants"
            ],
            list,
        )

        stored[
            "participants"
        ].append(
            "changed"
        )

        self.assertEqual(
            result.participants,
            (
                self.first.name,
                self.second.name,
            ),
        )

        fresh = (
            result.to_dict()
        )

        self.assertEqual(
            fresh[
                "participants"
            ],
            [
                self.first.name,
                self.second.name,
            ],
        )

    def test_social_interactions_are_detached_boundaries(
        self
    ):
        self.define_ritual()

        group = (
            self.groups.groups[
                self.group_id
            ]
        )

        result = (
            self.rituals.perform(
                self.group_id,
                "evening_patrol",
                [
                    self.first,
                    self.second,
                ],
            )
        )

        group_event = (
            group.history[
                -1
            ]
        )

        first_event = (
            self.first.social_interactions[
                -1
            ]
        )

        second_event = (
            self.second.social_interactions[
                -1
            ]
        )

        self.assertEqual(
            first_event,
            result.to_dict(),
        )

        self.assertEqual(
            second_event,
            result.to_dict(),
        )

        self.assertIsNot(
            first_event,
            group_event,
        )

        self.assertIsNot(
            second_event,
            group_event,
        )

        self.assertIsNot(
            first_event,
            second_event,
        )

        first_event[
            "participants"
        ].append(
            "changed"
        )

        self.assertEqual(
            second_event[
                "participants"
            ],
            [
                self.first.name,
                self.second.name,
            ],
        )

        self.assertEqual(
            result.participants,
            (
                self.first.name,
                self.second.name,
            ),
        )

    def test_results_are_immutable(
        self
    ):
        denied = (
            self.rituals.perform(
                self.group_id,
                "missing",
                [
                    self.first
                ],
            )
        )

        with self.assertRaises(
            AttributeError
        ):
            denied.reason = "changed"

        self.define_ritual()

        event = (
            self.rituals.perform(
                self.group_id,
                "evening_patrol",
                [
                    self.first
                ],
            )
        )

        with self.assertRaises(
            AttributeError
        ):
            event.strength = 0.0

        with self.assertRaises(
            AttributeError
        ):
            event.participants = ()


if __name__ == "__main__":
    unittest.main()
