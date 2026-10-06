import unittest

from cats.cat_cultural_adoption_result_state import (
    CatCulturalExposureDeniedResult,
    CatCulturalPreferenceAdoptedResult,
    CatCulturalPreferenceAdoptionDeniedResult,
    CatCulturalTraditionEvaluatedEvent,
    CatCulturalTraditionEvaluationResult,
)
from cats.cat_cultural_adoption_system import (
    CatCulturalAdoptionSystem,
)
from cats.cat_group_culture_system import (
    CatGroupCultureSystem,
)
from cats.cat_group_innovation_system import (
    CatGroupInnovationSystem,
)
from cats.cat_group_knowledge_system import (
    CatGroupKnowledgeSystem,
)
from cats.cat_group_myth_system import (
    CatGroupMythSystem,
)
from cats.cat_group_system import (
    CatGroupSystem,
)
from cats.cat_memetic_selection_result_state import (
    CatInnovationMemeticExposureResult,
    CatInnovationMemeticSelectionResult,
    CatMemeExposureDeniedResult,
    CatMythMemeticExposureResult,
    CatMythMemeticSelectionResult,
)
from cats.cat_memetic_selection_system import (
    CatMemeticSelectionSystem,
)
from cats.cats import Cats
from universe.universe import Universe


class CatCulturalAdoptionMemeticResultsObjectStateTests(
    unittest.TestCase
):

    def setUp(self):
        self.universe = Universe()

        self.cats = Cats(
            self.universe
        )

        self.first = self.cats.create_cat(
            name="object_first",
            color="black",
            fur_length="short",
        )

        self.second = self.cats.create_cat(
            name="object_second",
            color="white",
            fur_length="short",
        )

        self.groups = CatGroupSystem(
            self.cats
        )

        self.group_id = (
            self.groups.create_group(
                self.first,
                name="object_group",
            ).group_id
        )

        self.groups.add_member(
            self.group_id,
            self.second,
            self.cats.cats,
        )

        self.culture = (
            CatGroupCultureSystem(
                self.groups
            )
        )

        self.adoption = (
            CatCulturalAdoptionSystem(
                self.groups
            )
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

    def test_tradition_evaluation_returns_object(
        self
    ):
        missing = (
            self.adoption.evaluate_tradition(
                self.second,
                self.group_id,
                "missing",
            )
        )

        self.assertIsInstance(
            missing,
            CatCulturalTraditionEvaluationResult,
        )

        self.assertFalse(
            missing.known
        )

        self.assertFalse(
            missing.adopt
        )

        self.culture.practice(
            self.group_id,
            "night_patrol",
            "exploration",
            weight=0.8,
        )

        self.second.personality.traits.curiosity = (
            1.0
        )

        result = (
            self.adoption.evaluate_tradition(
                self.second,
                self.group_id,
                "night_patrol",
            )
        )

        self.assertIsInstance(
            result,
            CatCulturalTraditionEvaluationResult,
        )

        self.assertTrue(
            result.known
        )

        self.assertTrue(
            result.adopt
        )

        self.assertGreater(
            result.score,
            0.0,
        )

        self.assert_object_only(
            result
        )

    def test_tradition_exposure_returns_and_stores_event_object(
        self
    ):
        denied = (
            self.adoption.expose_to_tradition(
                self.second,
                self.group_id,
                "missing",
            )
        )

        self.assertIsInstance(
            denied,
            CatCulturalExposureDeniedResult,
        )

        self.assertFalse(
            denied.adopted
        )

        self.culture.practice(
            self.group_id,
            "night_patrol",
            "exploration",
            weight=0.8,
        )

        self.second.personality.traits.curiosity = (
            1.0
        )

        result = (
            self.adoption.expose_to_tradition(
                self.second,
                self.group_id,
                "night_patrol",
            )
        )

        stored = (
            self.second.social_interactions[
                -1
            ]
        )

        self.assertIsInstance(
            result,
            CatCulturalTraditionEvaluatedEvent,
        )

        self.assertTrue(
            result.adopted
        )

        self.assertIsInstance(
            stored,
            CatCulturalTraditionEvaluatedEvent,
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
            stored
        )

    def test_preference_adoption_returns_typed_results(
        self
    ):
        denied = (
            self.adoption.adopt_preference(
                self.second,
                self.group_id,
                "missing",
            )
        )

        self.assertIsInstance(
            denied,
            CatCulturalPreferenceAdoptionDeniedResult,
        )

        self.assertFalse(
            denied.adopted
        )

        self.culture.express_preference(
            self.group_id,
            "sleeping_place",
            "bar_cloth",
            strength=0.4,
        )

        result = (
            self.adoption.adopt_preference(
                self.second,
                self.group_id,
                "sleeping_place",
            )
        )

        self.assertIsInstance(
            result,
            CatCulturalPreferenceAdoptedResult,
        )

        self.assertTrue(
            result.adopted
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

    def create_memes(
        self
    ):
        knowledge = (
            CatGroupKnowledgeSystem(
                self.groups
            )
        )

        knowledge.contribute(
            self.group_id,
            self.first,
            "safe_route",
            {
                "route": "bar_to_library",
            },
            "navigation",
            confidence=1.0,
        )

        knowledge.contribute(
            self.group_id,
            self.first,
            "danger_scent",
            {
                "aroma": "cronenberg",
            },
            "danger",
            confidence=1.0,
        )

        myth_id = (
            CatGroupMythSystem(
                self.groups
            ).create_from_knowledge(
                self.group_id,
                "danger_scent",
            ).myth_id
        )

        innovation_id = (
            CatGroupInnovationSystem(
                self.groups
            ).combine(
                self.group_id,
                [
                    "safe_route",
                    "danger_scent",
                ],
                name="safe_scent_route",
                category="navigation",
                procedure={
                    "rule":
                        "avoid danger scent",
                },
            ).innovation_id
        )

        return (
            myth_id,
            innovation_id,
        )

    def test_myth_memetic_exposure_returns_object(
        self
    ):
        selection = (
            CatMemeticSelectionSystem(
                self.groups
            )
        )

        denied = selection.expose_myth(
            self.group_id,
            self.cats.cats,
            "missing",
        )

        self.assertIsInstance(
            denied,
            CatMemeExposureDeniedResult,
        )

        self.assertFalse(
            denied.exposed
        )

        myth_id, _ = self.create_memes()

        result = selection.expose_myth(
            self.group_id,
            self.cats.cats,
            myth_id,
        )

        self.assertIsInstance(
            result,
            CatMythMemeticExposureResult,
        )

        self.assertTrue(
            result.exposed
        )

        self.assertIsInstance(
            result.adopted,
            tuple,
        )

        self.assertIsInstance(
            result.rejected,
            tuple,
        )

        self.assertGreater(
            result.fitness,
            0.0,
        )

        self.assert_object_only(
            result
        )

    def test_innovation_memetic_exposure_returns_object(
        self
    ):
        selection = (
            CatMemeticSelectionSystem(
                self.groups
            )
        )

        denied = (
            selection.expose_innovation(
                self.group_id,
                self.cats.cats,
                "missing",
            )
        )

        self.assertIsInstance(
            denied,
            CatMemeExposureDeniedResult,
        )

        self.assertFalse(
            denied.exposed
        )

        _, innovation_id = (
            self.create_memes()
        )

        result = (
            selection.expose_innovation(
                self.group_id,
                self.cats.cats,
                innovation_id,
            )
        )

        self.assertIsInstance(
            result,
            CatInnovationMemeticExposureResult,
        )

        self.assertTrue(
            result.exposed
        )

        self.assertIsInstance(
            result.adopted,
            tuple,
        )

        self.assertIsInstance(
            result.rejected,
            tuple,
        )

        self.assertGreater(
            result.fitness,
            0.0,
        )

        self.assert_object_only(
            result
        )

    def test_myth_selection_returns_object(
        self
    ):
        myth_id, _ = self.create_memes()

        selection = (
            CatMemeticSelectionSystem(
                self.groups
            )
        )

        selection.expose_myth(
            self.group_id,
            self.cats.cats,
            myth_id,
        )

        result = selection.select_myths(
            self.group_id,
            minimum_fitness=0.1,
        )

        self.assertIsInstance(
            result,
            CatMythMemeticSelectionResult,
        )

        self.assertIsInstance(
            result.surviving,
            tuple,
        )

        self.assertIn(
            myth_id,
            result.surviving,
        )

        self.assert_object_only(
            result
        )

    def test_innovation_selection_returns_object(
        self
    ):
        _, innovation_id = (
            self.create_memes()
        )

        selection = (
            CatMemeticSelectionSystem(
                self.groups
            )
        )

        selection.expose_innovation(
            self.group_id,
            self.cats.cats,
            innovation_id,
        )

        result = (
            selection.select_innovations(
                self.group_id,
                minimum_fitness=0.1,
            )
        )

        self.assertIsInstance(
            result,
            CatInnovationMemeticSelectionResult,
        )

        self.assertIsInstance(
            result.surviving,
            tuple,
        )

        self.assertIn(
            innovation_id,
            result.surviving,
        )

        self.assert_object_only(
            result
        )


if __name__ == "__main__":
    unittest.main()
