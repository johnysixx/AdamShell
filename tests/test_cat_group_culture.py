import unittest

from universe.universe import Universe
from cats.cats import Cats
from cats.cat_group_system import (
    CatGroupSystem
)
from cats.cat_group_knowledge_system import (
    CatGroupKnowledgeSystem
)
from cats.cat_group_culture_system import (
    CatGroupCultureSystem
)
from cats.cat_group_myth_system import (
    CatGroupMythSystem
)
from cats.cat_group_innovation_system import (
    CatGroupInnovationSystem
)


class CatGroupCultureTests(
    unittest.TestCase
):

    def setUp(self):
        self.universe = Universe()

        self.cats = Cats(
            self.universe
        )

        self.cat = self.cats.create_cat(
            name="pazuzu",
            color="black",
            fur_length="short"
        )

        self.other = self.cats.create_cat(
            name="other",
            color="white",
            fur_length="short"
        )

        self.groups = CatGroupSystem(
            self.cats
        )

        self.group_id = (
            self.groups.create_group(
                self.cat,
                name="bar_cats"
            )[
                "group_id"
            ]
        )

        self.knowledge = (
            CatGroupKnowledgeSystem(
                self.groups
            )
        )

    def _knowledge(
        self
    ):
        self.knowledge.contribute(
            self.group_id,
            self.cat,
            knowledge_id="safe_route",
            content={
                "from": "bar",
                "to": "library"
            },
            category="navigation",
            confidence=0.9,
            verified=True
        )

        self.knowledge.contribute(
            self.group_id,
            self.cat,
            knowledge_id="cronenberg_scent",
            content={
                "aroma": "cronenberg",
                "danger": True
            },
            category="danger",
            confidence=0.8,
            verified=True
        )

    def test_repeated_practice_becomes_tradition(
        self
    ):
        culture = CatGroupCultureSystem(
            self.groups
        )

        for _ in range(5):
            culture.practice(
                self.group_id,
                practice="evening_box_patrol",
                category="exploration",
                participants=[
                    self.cat.name
                ],
                weight=0.12
            )

        profile = culture.profile(
            self.group_id
        )

        self.assertEqual(
            profile.traditions[
                "evening_box_patrol"
            ][
                "occurrences"
            ],
            5
        )

        self.assertGreater(
            profile.traits[
                "curious"
            ],
            0.0
        )

    def test_group_can_develop_preference(
        self
    ):
        culture = CatGroupCultureSystem(
            self.groups
        )

        culture.express_preference(
            self.group_id,
            preference="sleeping_place",
            value="bar_cloth",
            strength=0.4
        )

        profile = culture.profile(
            self.group_id
        )

        self.assertEqual(
            profile.preferences[
                "sleeping_place"
            ][
                "value"
            ],
            "bar_cloth"
        )

    def test_group_can_create_myth_from_knowledge(
        self
    ):
        self._knowledge()

        myths = CatGroupMythSystem(
            self.groups
        )

        result = myths.create_from_knowledge(
            self.group_id,
            "cronenberg_scent",
            title=(
                "The Smell Beyond the Box"
            ),
            interpretation={
                "claim": (
                    "where the smell appears, "
                    "the monster follows"
                )
            }
        )

        self.assertTrue(
            result["created"]
        )

        myth = self.groups.groups[self.group_id].myths[
            result[
                "myth_id"
            ]
        ]

        self.assertFalse(
            myth.verified
        )

    def test_myth_can_change_during_retelling(
        self
    ):
        self._knowledge()

        second_group = (
            self.groups.create_group(
                self.other,
                name="other_group"
            )[
                "group_id"
            ]
        )

        myths = CatGroupMythSystem(
            self.groups
        )

        created = myths.create_from_knowledge(
            self.group_id,
            "cronenberg_scent"
        )

        result = myths.retell(
            self.group_id,
            second_group,
            created[
                "myth_id"
            ],
            transformation={
                "claim": (
                    "all strange boxes contain "
                    "a cronenberg"
                )
            }
        )

        self.assertTrue(
            result["retold"]
        )

        self.assertTrue(
            result["transformed"]
        )

        received = (
            self.groups.groups[second_group].myths[
                result[
                    "myth_id"
                ]
            ]
        )

        self.assertNotEqual(
            result[
                "myth_id"
            ],
            created[
                "myth_id"
            ]
        )

        self.assertEqual(
            received.parent_version,
            created[
                "myth_id"
            ]
        )

        self.assertEqual(
            received.transformations,
            1
        )

    def test_myth_can_be_told_to_individual_cats(
        self
    ):
        self._knowledge()

        self.groups.add_member(
            self.group_id,
            self.other,
            self.cats.cats
        )

        myths = CatGroupMythSystem(
            self.groups
        )

        created = myths.create_from_knowledge(
            self.group_id,
            "safe_route"
        )

        myths.tell_members(
            self.group_id,
            self.cats.cats,
            created[
                "myth_id"
            ]
        )

        self.assertIn(
            created[
                "myth_id"
            ],
            self.other.knowledge[
                "heard_group_myths"
            ]
        )

    def test_two_knowledge_sources_can_create_innovation(
        self
    ):
        self._knowledge()

        innovation = (
            CatGroupInnovationSystem(
                self.groups
            )
        )

        result = innovation.combine(
            self.group_id,
            knowledge_ids=[
                "safe_route",
                "cronenberg_scent"
            ],
            name="scent_safe_navigation",
            category="navigation",
            procedure={
                "rule": (
                    "follow safe route unless "
                    "cronenberg scent is detected"
                )
            }
        )

        self.assertTrue(
            result["created"]
        )

        self.assertIn(
            result[
                "innovation_id"
            ],
            self.groups.groups[self.group_id].knowledge
        )

    def test_successful_trials_can_verify_innovation(
        self
    ):
        self._knowledge()

        innovation = (
            CatGroupInnovationSystem(
                self.groups
            )
        )

        created = innovation.combine(
            self.group_id,
            knowledge_ids=[
                "safe_route",
                "cronenberg_scent"
            ],
            name="scent_safe_navigation",
            category="navigation",
            procedure={
                "rule": "avoid danger scent"
            }
        )

        innovation_id = created[
            "innovation_id"
        ]

        for _ in range(3):
            innovation.trial(
                self.group_id,
                innovation_id,
                success=True
            )

        record = (
            self.groups.groups[self.group_id].innovations[
                innovation_id
            ]
        )

        self.assertTrue(
            record.verified
        )


if __name__ == "__main__":
    unittest.main()
