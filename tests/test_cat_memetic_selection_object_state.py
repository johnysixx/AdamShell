import unittest

from universe.universe import Universe
from cats.cats import Cats
from cats.cat_group_system import (
    CatGroupSystem
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
from cats.cat_memetic_selection_state import (
    CatMemeticSelectionState
)


class CatMemeticSelectionObjectStateTests(
    unittest.TestCase
):

    def setUp(self):
        self.universe = Universe()

        self.cats = Cats(
            self.universe
        )

        self.cat = self.cats.create_cat(
            name='memetic_state_cat',
            color='black',
            fur_length='short',
        )

        self.cat.personality.traits.curiosity = 1.0
        self.cat.personality.traits.sociability = 1.0
        self.cat.intellect.normalized = 1.0

        self.groups = CatGroupSystem(
            self.cats
        )

        self.group_id = (
            self.groups.create_group(
                self.cat,
                name='memetic_state_group',
            )[
                'group_id'
            ]
        )

        knowledge = (
            CatGroupKnowledgeSystem(
                self.groups
            )
        )

        knowledge.contribute(
            self.group_id,
            self.cat,
            'danger_scent',
            {
                'aroma':
                    'cronenberg'
            },
            'danger',
            confidence=1.0,
        )

        knowledge.contribute(
            self.group_id,
            self.cat,
            'safe_route',
            {
                'route':
                    'bar_to_library'
            },
            'navigation',
            confidence=1.0,
        )

        myths = CatGroupMythSystem(
            self.groups
        )

        self.myth_id = (
            myths.create_from_knowledge(
                self.group_id,
                'danger_scent',
            )[
                'myth_id'
            ]
        )

        innovations = (
            CatGroupInnovationSystem(
                self.groups
            )
        )

        self.innovation_id = (
            innovations.combine(
                self.group_id,
                [
                    'safe_route',
                    'danger_scent',
                ],
                name='safe_scent_route',
                category='navigation',
                procedure={
                    'rule':
                        'avoid danger scent'
                },
            )[
                'innovation_id'
            ]
        )

        self.selection = (
            CatMemeticSelectionSystem(
                self.groups
            )
        )

    def test_state_has_no_mapping_api(
        self
    ):
        state = CatMemeticSelectionState(
            group_id='group',
            score=0.75,
        )

        self.assertFalse(
            hasattr(
                state,
                'get',
            )
        )

        self.assertFalse(
            hasattr(
                state,
                '__getitem__',
            )
        )

        self.assertFalse(
            hasattr(
                state,
                '__setitem__',
            )
        )

    def test_myth_registry_stores_object_record(
        self
    ):
        self.selection.expose_myth(
            self.group_id,
            self.cats.cats,
            self.myth_id,
        )

        state = self.cat.culture.myths[
            self.myth_id
        ]

        self.assertIsInstance(
            state,
            CatMemeticSelectionState,
        )

        self.assertEqual(
            state.group_id,
            self.group_id,
        )

        self.assertGreater(
            state.score,
            0.0,
        )

    def test_innovation_registry_stores_object_record(
        self
    ):
        self.selection.expose_innovation(
            self.group_id,
            self.cats.cats,
            self.innovation_id,
        )

        state = (
            self.cat
            .culture
            .innovations[
                self.innovation_id
            ]
        )

        self.assertIsInstance(
            state,
            CatMemeticSelectionState,
        )

        self.assertEqual(
            state.group_id,
            self.group_id,
        )

        self.assertGreater(
            state.score,
            0.0,
        )

    def test_repeated_exposure_reuses_same_object(
        self
    ):
        self.selection.expose_myth(
            self.group_id,
            self.cats.cats,
            self.myth_id,
        )

        stored = self.cat.culture.myths[
            self.myth_id
        ]

        self.selection.expose_myth(
            self.group_id,
            self.cats.cats,
            self.myth_id,
        )

        current = self.cat.culture.myths[
            self.myth_id
        ]

        self.assertIs(
            current,
            stored,
        )

    def test_legacy_mapping_record_is_rejected(
        self
    ):
        self.cat.culture.myths[
            self.myth_id
        ] = {
            'score': 1.0,
            'group_id': self.group_id,
        }

        exposure_count = (
            self.cat.culture.exposures
        )

        with self.assertRaises(
            TypeError
        ):
            self.selection.expose_myth(
                self.group_id,
                self.cats.cats,
                self.myth_id,
            )

        self.assertEqual(
            self.cat.culture.exposures,
            exposure_count,
        )


if __name__ == '__main__':
    unittest.main()
