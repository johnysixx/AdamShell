import unittest

from cats.cat_group_culture_history_state import (
    CatGroupCulturalPracticeEvent,
    CatGroupPreferenceExpressedResult,
)
from cats.cat_group_culture_system import (
    CatGroupCultureSystem,
)
from cats.cat_group_cultural_conflict_state import (
    CatCulturalPreferenceConflict,
    CatGroupCulturalComparisonResult,
    CatGroupCulturalInteractionEvent,
)
from cats.cat_group_cultural_conflict_system import (
    CatGroupCulturalConflictSystem,
)
from cats.cat_group_diplomatic_lifecycle import (
    CatGroupDiplomaticLifecycle,
)
from cats.cat_group_diplomatic_lifecycle_state import (
    CatGroupBetrayalRecoveredResult,
    CatGroupBetrayalRecoveryDeniedResult,
    CatGroupBetrayalRecoverySkippedResult,
    CatGroupDiplomacyDecaySkippedResult,
    CatGroupDiplomacyMemoryAgedEvent,
    CatGroupMemorySnapshot,
)
from cats.cat_group_diplomacy_system import (
    CatGroupDiplomacySystem,
)
from cats.cat_group_institution_system import (
    CatGroupInstitutionSystem,
)
from cats.cat_group_institutional_conflict_escalation_state import (
    CatGroupInstitutionalConflictEvent,
)
from cats.cat_group_institutional_conflict_mediation_state import (
    CatInstitutionConflictMediatedEvent,
)
from cats.cat_group_institutional_conflict_system import (
    CatGroupInstitutionalConflictSystem,
)
from cats.cat_group_memory_state import (
    CatGroupMemoryState,
)
from cats.cat_group_role_system import (
    CatGroupRoleSystem,
)
from cats.cat_group_system import (
    CatGroupSystem,
)
from cats.cats import Cats
from universe.universe import Universe


class CatGroupCulturalDiplomacyHistoryObjectStateTests(
    unittest.TestCase
):

    def setUp(self):
        self.universe = Universe()

        self.cats = Cats(
            self.universe
        )

        self.first = self.cats.create_cat(
            name="diplomacy_first",
            color="black",
            fur_length="short",
        )

        self.second = self.cats.create_cat(
            name="diplomacy_second",
            color="white",
            fur_length="short",
        )

        self.mediator = self.cats.create_cat(
            name="diplomacy_mediator",
            color="gray",
            fur_length="short",
        )

        self.groups = CatGroupSystem(
            self.cats
        )

        self.first_group = (
            self.groups.create_group(
                self.first,
                name="first_group",
            ).group_id
        )

        self.second_group = (
            self.groups.create_group(
                self.second,
                name="second_group",
            ).group_id
        )

        self.groups.add_member(
            self.first_group,
            self.mediator,
            self.cats.cats,
        )

    def assert_object_only(
        self,
        value,
    ):
        for method_name in (
            "get",
            "keys",
            "items",
            "values",
            "to_dict",
        ):
            self.assertFalse(
                hasattr(
                    value,
                    method_name,
                )
            )

        with self.assertRaises(
            TypeError
        ):
            _ = value[
                "name"
            ]

    def test_cultural_practice_histories_are_objects(
        self
    ):
        culture = CatGroupCultureSystem(
            self.groups
        )

        result = culture.practice(
            self.first_group,
            "night_patrol",
            "exploration",
            participants=[
                self.first.name,
                self.mediator.name,
            ],
            weight=0.2,
        )

        group = self.groups.groups[
            self.first_group
        ]

        culture_event = (
            group.culture.history[
                -1
            ]
        )

        group_event = (
            group.history[
                -1
            ]
        )

        self.assertIsInstance(
            result,
            CatGroupCulturalPracticeEvent,
        )

        for event in (
            culture_event,
            group_event,
        ):
            self.assertIsInstance(
                event,
                CatGroupCulturalPracticeEvent,
            )

            self.assertEqual(
                event,
                result,
            )

            self.assertIsNot(
                event,
                result,
            )

            self.assert_object_only(
                event
            )

        self.assertIsNot(
            culture_event,
            group_event,
        )

    def test_preference_expression_returns_object(
        self
    ):
        result = CatGroupCultureSystem(
            self.groups
        ).express_preference(
            self.first_group,
            "sleeping_place",
            "bar_cloth",
            strength=0.4,
        )

        self.assertIsInstance(
            result,
            CatGroupPreferenceExpressedResult,
        )

        self.assertTrue(
            result.expressed
        )

        self.assertEqual(
            result.preference,
            "sleeping_place",
        )

        self.assertEqual(
            result.value,
            "bar_cloth",
        )

        self.assert_object_only(
            result
        )

    def test_cultural_comparison_is_nested_object_state(
        self
    ):
        culture = CatGroupCultureSystem(
            self.groups
        )

        culture.express_preference(
            self.first_group,
            "sleeping_place",
            "bar_cloth",
            strength=0.8,
        )

        culture.express_preference(
            self.second_group,
            "sleeping_place",
            "window",
            strength=0.8,
        )

        result = CatGroupCulturalConflictSystem(
            self.groups
        ).compare(
            self.first_group,
            self.second_group,
        )

        self.assertIsInstance(
            result,
            CatGroupCulturalComparisonResult,
        )

        self.assertGreater(
            result.conflict_score,
            0.0,
        )

        self.assertIsInstance(
            result.preference_conflicts,
            tuple,
        )

        conflict = (
            result.preference_conflicts[
                0
            ]
        )

        self.assertIsInstance(
            conflict,
            CatCulturalPreferenceConflict,
        )

        self.assertEqual(
            conflict.preference,
            "sleeping_place",
        )

        self.assert_object_only(
            result
        )

        self.assert_object_only(
            conflict
        )

    def test_cultural_interaction_histories_are_objects(
        self
    ):
        diplomacy = CatGroupDiplomacySystem(
            self.groups
        )

        diplomacy.evaluate(
            self.first_group,
            self.second_group,
        )

        diplomacy.evaluate(
            self.second_group,
            self.first_group,
        )

        result = CatGroupCulturalConflictSystem(
            self.groups
        ).interact(
            self.first_group,
            self.second_group,
        )

        first_event = (
            self.groups.groups[
                self.first_group
            ].history[
                -1
            ]
        )

        second_event = (
            self.groups.groups[
                self.second_group
            ].history[
                -1
            ]
        )

        self.assertIsInstance(
            result,
            CatGroupCulturalInteractionEvent,
        )

        for event in (
            first_event,
            second_event,
        ):
            self.assertIsInstance(
                event,
                CatGroupCulturalInteractionEvent,
            )

            self.assertEqual(
                event,
                result,
            )

            self.assertIsNot(
                event,
                result,
            )

            self.assert_object_only(
                event
            )

        self.assertIsNot(
            first_event,
            second_event,
        )

    def test_diplomacy_decay_without_memory_returns_object(
        self
    ):
        result = CatGroupDiplomaticLifecycle(
            self.groups
        ).advance_relation(
            self.first_group,
            self.second_group,
        )

        self.assertIsInstance(
            result,
            CatGroupDiplomacyDecaySkippedResult,
        )

        self.assertFalse(
            result.advanced
        )

        self.assertEqual(
            result.reason,
            "no_shared_history",
        )

        self.assert_object_only(
            result
        )

    def test_diplomacy_aging_uses_memory_snapshots(
        self
    ):
        group = self.groups.groups[
            self.first_group
        ]

        group.group_memory[
            self.second_group
        ] = CatGroupMemoryState(
            encounters=2,
            peaceful_encounters=1,
            conflicts=2,
            defeats=1,
            cooperations=2,
        )

        live_memory = (
            group.group_memory[
                self.second_group
            ]
        )

        result = CatGroupDiplomaticLifecycle(
            self.groups
        ).advance_relation(
            self.first_group,
            self.second_group,
        )

        stored = group.history[
            -1
        ]

        self.assertIsInstance(
            result,
            CatGroupDiplomacyMemoryAgedEvent,
        )

        self.assertIsInstance(
            result.before,
            CatGroupMemorySnapshot,
        )

        self.assertIsInstance(
            result.after,
            CatGroupMemorySnapshot,
        )

        self.assertEqual(
            result.before.conflicts,
            2,
        )

        self.assertEqual(
            result.after.conflicts,
            1,
        )

        self.assertEqual(
            live_memory.conflicts,
            1,
        )

        self.assertIsInstance(
            stored,
            CatGroupDiplomacyMemoryAgedEvent,
        )

        self.assertEqual(
            stored,
            result,
        )

        self.assertIsNot(
            stored,
            result,
        )

        self.assert_object_only(
            result
        )

        self.assert_object_only(
            result.before
        )

    def test_betrayal_recovery_returns_typed_results(
        self
    ):
        lifecycle = (
            CatGroupDiplomaticLifecycle(
                self.groups
            )
        )

        denied = (
            lifecycle.recover_from_betrayal(
                self.first_group,
                self.second_group,
            )
        )

        self.assertIsInstance(
            denied,
            CatGroupBetrayalRecoveryDeniedResult,
        )

        group = self.groups.groups[
            self.first_group
        ]

        memory = CatGroupMemoryState()

        group.group_memory[
            self.second_group
        ] = memory

        skipped = (
            lifecycle.recover_from_betrayal(
                self.first_group,
                self.second_group,
            )
        )

        self.assertIsInstance(
            skipped,
            CatGroupBetrayalRecoverySkippedResult,
        )

        memory.betrayals = 1
        memory.cooperations = 2

        insufficient = (
            lifecycle.recover_from_betrayal(
                self.first_group,
                self.second_group,
            )
        )

        self.assertIsInstance(
            insufficient,
            CatGroupBetrayalRecoveryDeniedResult,
        )

        self.assertEqual(
            insufficient.reason,
            "insufficient_new_cooperation",
        )

        memory.cooperations = 3

        recovered = (
            lifecycle.recover_from_betrayal(
                self.first_group,
                self.second_group,
            )
        )

        self.assertIsInstance(
            recovered,
            CatGroupBetrayalRecoveredResult,
        )

        self.assertTrue(
            recovered.recovered
        )

        self.assertEqual(
            recovered.remaining_betrayals,
            0,
        )

        self.assert_object_only(
            recovered
        )

    def _institutional_conflict(
        self,
        intensity=0.4,
    ):
        institutions = (
            CatGroupInstitutionSystem(
                self.groups
            )
        )

        institutions.establish(
            self.first_group,
            "night_watch",
            "protect_group",
            roles=[],
            rituals=[],
        )

        institutions.establish(
            self.first_group,
            "door_watch",
            "control_door",
            roles=[],
            rituals=[],
        )

        conflicts = (
            CatGroupInstitutionalConflictSystem(
                self.groups
            )
        )

        result = conflicts.escalate(
            self.first_group,
            "night_watch",
            "door_watch",
            issue="attention",
            intensity=intensity,
        )

        return (
            conflicts,
            result,
        )

    def test_institutional_conflict_histories_are_objects(
        self
    ):
        conflicts, result = (
            self._institutional_conflict()
        )

        group = self.groups.groups[
            self.first_group
        ]

        conflict = (
            group.institution_conflicts[
                result.conflict_id
            ]
        )

        conflict_event = (
            conflict.history[
                -1
            ]
        )

        group_event = (
            group.history[
                -1
            ]
        )

        self.assertIsInstance(
            result,
            CatGroupInstitutionalConflictEvent,
        )

        for event in (
            conflict_event,
            group_event,
        ):
            self.assertIsInstance(
                event,
                CatGroupInstitutionalConflictEvent,
            )

            self.assertEqual(
                event,
                result,
            )

            self.assertIsNot(
                event,
                result,
            )

            self.assert_object_only(
                event
            )

        self.assertIsNot(
            conflict_event,
            group_event,
        )

    def test_institutional_mediation_histories_are_objects(
        self
    ):
        conflicts, created = (
            self._institutional_conflict()
        )

        self.mediator.personality.traits.sociability = (
            1.0
        )

        self.mediator.group.influence = (
            1.0
        )

        assigned = CatGroupRoleSystem(
            self.groups
        ).assign(
            self.first_group,
            self.mediator,
            "mediator",
        )

        self.assertTrue(
            assigned.assigned
        )

        result = conflicts.mediate(
            self.first_group,
            created.conflict_id,
            self.mediator,
        )

        group = self.groups.groups[
            self.first_group
        ]

        conflict = (
            group.institution_conflicts[
                created.conflict_id
            ]
        )

        conflict_event = (
            conflict.history[
                -1
            ]
        )

        group_event = (
            group.history[
                -1
            ]
        )

        self.assertIsInstance(
            result,
            CatInstitutionConflictMediatedEvent,
        )

        for event in (
            conflict_event,
            group_event,
        ):
            self.assertIsInstance(
                event,
                CatInstitutionConflictMediatedEvent,
            )

            self.assertEqual(
                event,
                result,
            )

            self.assertIsNot(
                event,
                result,
            )

            self.assert_object_only(
                event
            )

        self.assertIsNot(
            conflict_event,
            group_event,
        )


if __name__ == "__main__":
    unittest.main()
