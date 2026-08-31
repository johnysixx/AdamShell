import unittest

from universe.universe import Universe
from cats.cats import Cats
from cats.cat_group_system import (
    CatGroupSystem
)
from cats.cat_group_culture_system import (
    CatGroupCultureSystem
)
from cats.cat_group_cultural_inheritance_system import (
    CatGroupCulturalInheritanceSystem
)
from cats.cat_group_split_system import (
    CatGroupSplitSystem
)
from cats.cat_group_knowledge_system import (
    CatGroupKnowledgeSystem
)
from cats.cat_group_myth_system import (
    CatGroupMythSystem
)
from cats.cat_group_innovation_system import (
    CatGroupInnovationSystem
)
from cats.cat_group_innovation_tree_system import (
    CatGroupInnovationTreeSystem
)


class CatGroupCulturalEvolutionTests(
    unittest.TestCase
):

    def setUp(self):
        self.universe = Universe()

        self.cats = Cats(
            self.universe
        )

        self.members = []

        for index in range(4):
            cat = self.cats.create_cat(
                name=f"cat_{index}",
                color="black",
                fur_length="short"
            )

            self.members.append(
                cat
            )

        self.groups = CatGroupSystem(
            self.cats
        )

        created = self.groups.create_group(
            self.members[0],
            name="parent"
        )

        self.parent = created[
            "group_id"
        ]

        for cat in self.members[1:]:
            self.groups.add_member(
                self.parent,
                cat,
                self.cats.cats
            )

    def _knowledge(
        self
    ):
        knowledge = (
            CatGroupKnowledgeSystem(
                self.groups
            )
        )

        knowledge.contribute(
            self.parent,
            self.members[0],
            "safe_route",
            {
                "route": "bar_to_library"
            },
            "navigation",
            confidence=1.0
        )

        knowledge.contribute(
            self.parent,
            self.members[0],
            "danger_scent",
            {
                "aroma": "cronenberg"
            },
            "danger",
            confidence=1.0
        )

    def test_daughter_group_inherits_culture(
        self
    ):
        culture = CatGroupCultureSystem(
            self.groups
        )

        for _ in range(4):
            culture.practice(
                self.parent,
                "night_patrol",
                "exploration",
                weight=0.2
            )

        split = CatGroupSplitSystem(
            self.groups
        )

        result = split.split(
            self.parent,
            self.cats.cats,
            departing_members=[
                self.members[2].name,
                self.members[3].name
            ],
            new_name="daughter"
        )

        daughter = result[
            "daughter_group"
        ]

        self.assertIn(
            "night_patrol",
            self.groups.groups[daughter].culture.traditions
        )

        self.assertEqual(
            self.groups.groups[daughter].cultural_parent_group,
            self.parent
        )

    def test_daughter_culture_can_diverge(
        self
    ):
        culture = CatGroupCultureSystem(
            self.groups
        )

        culture.practice(
            self.parent,
            "night_patrol",
            "exploration",
            weight=0.5
        )

        split = CatGroupSplitSystem(
            self.groups
        )

        result = split.split(
            self.parent,
            self.cats.cats,
            departing_members=[
                self.members[2].name,
                self.members[3].name
            ],
            new_name="daughter"
        )

        daughter = result[
            "daughter_group"
        ]

        culture.practice(
            daughter,
            "defend_window",
            "defense",
            weight=0.7
        )

        inheritance = (
            CatGroupCulturalInheritanceSystem(
                self.groups
            )
        )

        divergence = inheritance.divergence(
            self.parent,
            daughter
        )

        self.assertGreater(
            divergence[
                "divergence"
            ],
            0.0
        )

    def test_transformed_myth_gets_new_version(
        self
    ):
        self._knowledge()

        other_cat = self.cats.create_cat(
            name="other_cat",
            color="white",
            fur_length="short"
        )

        second = self.groups.create_group(
            other_cat,
            name="second"
        )[
            "group_id"
        ]

        myths = CatGroupMythSystem(
            self.groups
        )

        created = myths.create_from_knowledge(
            self.parent,
            "danger_scent"
        )

        result = myths.retell(
            self.parent,
            second,
            created[
                "myth_id"
            ],
            transformation={
                "claim": "all boxes are dangerous"
            }
        )

        self.assertNotEqual(
            result[
                "myth_id"
            ],
            created[
                "myth_id"
            ]
        )

        child = self.groups.groups[second].myths[
            result[
                "myth_id"
            ]
        ]

        self.assertEqual(
            child.parent_version,
            created[
                "myth_id"
            ]
        )

        self.assertEqual(
            child.generation,
            1
        )

    def test_innovation_can_have_descendant(
        self
    ):
        self._knowledge()

        innovation = (
            CatGroupInnovationSystem(
                self.groups
            )
        )

        first = innovation.combine(
            self.parent,
            [
                "safe_route",
                "danger_scent"
            ],
            name="safe_scent_route",
            category="navigation",
            procedure={
                "rule": "avoid danger scent"
            }
        )

        second = innovation.combine(
            self.parent,
            [
                "safe_route",
                "danger_scent"
            ],
            name="adaptive_safe_scent_route",
            category="navigation",
            procedure={
                "rule": (
                    "change route when danger "
                    "scent strengthens"
                )
            },
            parent_innovation_id=(
                first[
                    "innovation_id"
                ]
            )
        )

        tree = CatGroupInnovationTreeSystem(
            self.groups
        )

        descendants = tree.descendants(
            self.parent,
            first[
                "innovation_id"
            ]
        )

        self.assertIn(
            second[
                "innovation_id"
            ],
            descendants
        )

        record = self.groups.groups[self.parent].innovations[
            second[
                "innovation_id"
            ]
        ]

        self.assertEqual(
            record.generation,
            1
        )


if __name__ == "__main__":
    unittest.main()
