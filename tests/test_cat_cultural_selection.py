import unittest

from universe.universe import Universe
from cats.cats import Cats
from cats.cat_group_system import (
    CatGroupSystem
)
from cats.cat_group_culture_system import (
    CatGroupCultureSystem
)
from cats.cat_cultural_adoption_system import (
    CatCulturalAdoptionSystem
)
from cats.cat_group_cultural_conflict_system import (
    CatGroupCulturalConflictSystem
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
from cats.cat_memetic_selection_system import (
    CatMemeticSelectionSystem
)


class CatCulturalSelectionTests(
    unittest.TestCase
):

    def setUp(self):
        self.universe = Universe()

        self.cats = Cats(
            self.universe
        )

        self.first = self.cats.create_cat(
            name="first",
            color="black",
            fur_length="short"
        )

        self.second = self.cats.create_cat(
            name="second",
            color="white",
            fur_length="short"
        )

        self.third = self.cats.create_cat(
            name="third",
            color="gray",
            fur_length="short"
        )

        self.groups = CatGroupSystem(
            self.cats
        )

        self.first_group = (
            self.groups.create_group(
                self.first,
                name="first_group"
            )[
                "group_id"
            ]
        )

        self.groups.add_member(
            self.first_group,
            self.second,
            self.cats.cats
        )

        self.second_group = (
            self.groups.create_group(
                self.third,
                name="second_group"
            )[
                "group_id"
            ]
        )

    def test_cat_can_adopt_group_tradition(
        self
    ):
        culture = CatGroupCultureSystem(
            self.groups
        )

        culture.practice(
            self.first_group,
            "night_patrol",
            "exploration",
            weight=0.8
        )

        self.second.personality.setdefault(
            "traits",
            {}
        )[
            "curiosity"
        ] = 1.0

        adoption = CatCulturalAdoptionSystem(
            self.groups
        )

        result = adoption.expose_to_tradition(
            self.second,
            self.first_group,
            "night_patrol"
        )

        self.assertTrue(
            result["adopted"]
        )

        self.assertIn(
            "night_patrol",
            self.second.culture[
                "adopted_traditions"
            ]
        )

    def test_cat_can_reject_weak_tradition(
        self
    ):
        culture = CatGroupCultureSystem(
            self.groups
        )

        culture.practice(
            self.first_group,
            "dangerous_box_jump",
            "exploration",
            weight=0.01
        )

        self.second.personality.setdefault(
            "traits",
            {}
        )[
            "curiosity"
        ] = 0.0

        adoption = CatCulturalAdoptionSystem(
            self.groups
        )

        result = adoption.expose_to_tradition(
            self.second,
            self.first_group,
            "dangerous_box_jump"
        )

        self.assertFalse(
            result["adopted"]
        )

    def test_conflicting_preferences_create_friction(
        self
    ):
        culture = CatGroupCultureSystem(
            self.groups
        )

        culture.express_preference(
            self.first_group,
            "sleeping_place",
            "bar_cloth",
            strength=0.8
        )

        culture.express_preference(
            self.second_group,
            "sleeping_place",
            "window",
            strength=0.8
        )

        conflict = (
            CatGroupCulturalConflictSystem(
                self.groups
            )
        )

        result = conflict.compare(
            self.first_group,
            self.second_group
        )

        self.assertGreater(
            result[
                "conflict_score"
            ],
            0.0
        )

        self.assertGreaterEqual(
            len(
                result[
                    "preference_conflicts"
                ]
            ),
            1
        )

    def _create_myth_and_innovation(
        self
    ):
        knowledge = CatGroupKnowledgeSystem(
            self.groups
        )

        knowledge.contribute(
            self.first_group,
            self.first,
            "safe_route",
            {
                "route": "bar_to_library"
            },
            "navigation",
            confidence=1.0
        )

        knowledge.contribute(
            self.first_group,
            self.first,
            "danger_scent",
            {
                "aroma": "cronenberg"
            },
            "danger",
            confidence=1.0
        )

        myths = CatGroupMythSystem(
            self.groups
        )

        myth = myths.create_from_knowledge(
            self.first_group,
            "danger_scent"
        )

        innovations = (
            CatGroupInnovationSystem(
                self.groups
            )
        )

        innovation = innovations.combine(
            self.first_group,
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

        return (
            myth[
                "myth_id"
            ],
            innovation[
                "innovation_id"
            ]
        )

    def test_myths_gain_memetic_fitness_from_adoption(
        self
    ):
        myth_id, _ = (
            self._create_myth_and_innovation()
        )

        selection = (
            CatMemeticSelectionSystem(
                self.groups
            )
        )

        result = selection.expose_myth(
            self.first_group,
            self.cats.cats,
            myth_id
        )

        self.assertTrue(
            result["exposed"]
        )

        self.assertGreater(
            result["fitness"],
            0.0
        )

    def test_innovations_gain_memetic_fitness(
        self
    ):
        _, innovation_id = (
            self._create_myth_and_innovation()
        )

        selection = (
            CatMemeticSelectionSystem(
                self.groups
            )
        )

        result = (
            selection.expose_innovation(
                self.first_group,
                self.cats.cats,
                innovation_id
            )
        )

        self.assertTrue(
            result["exposed"]
        )

        self.assertGreater(
            result["fitness"],
            0.0
        )

    def test_memetic_selection_distinguishes_survival(
        self
    ):
        myth_id, innovation_id = (
            self._create_myth_and_innovation()
        )

        selection = (
            CatMemeticSelectionSystem(
                self.groups
            )
        )

        selection.expose_myth(
            self.first_group,
            self.cats.cats,
            myth_id
        )

        selection.expose_innovation(
            self.first_group,
            self.cats.cats,
            innovation_id
        )

        myths = selection.select_myths(
            self.first_group,
            minimum_fitness=0.10
        )

        innovations = (
            selection.select_innovations(
                self.first_group,
                minimum_fitness=0.10
            )
        )

        self.assertIn(
            myth_id,
            myths[
                "surviving"
            ]
        )

        self.assertIn(
            innovation_id,
            innovations[
                "surviving"
            ]
        )


if __name__ == "__main__":
    unittest.main()
