import unittest

from cats.cat_group_norm_definition_state import (
    CatGroupNormDefinedEvent,
)
from cats.cat_group_norm_system import (
    CatGroupNormSystem,
)
from cats.cat_group_system import (
    CatGroupSystem,
)
from cats.cats import Cats
from universe.universe import Universe


class CatGroupNormDefinitionObjectStateTests(
    unittest.TestCase
):

    def setUp(self):
        self.universe = Universe()

        self.cats = Cats(
            self.universe
        )

        self.founder = (
            self.cats.create_cat(
                name="founder",
                color="black",
                fur_length="short",
            )
        )

        self.groups = (
            CatGroupSystem(
                self.cats
            )
        )

        created_group = (
            self.groups.create_group(
                self.founder,
                name="bar_cats",
            )
        )

        self.group_id = (
            created_group[
                "group_id"
            ]
        )

        self.norms = (
            CatGroupNormSystem(
                self.groups
            )
        )

    def test_define_returns_event_object(
        self
    ):
        result = (
            self.norms.define(
                self.group_id,
                "protect_kittens",
                "protective",
                {
                    "action": "protect",
                    "target": "kitten",
                },
                importance=0.9,
            )
        )

        self.assertIsInstance(
            result,
            CatGroupNormDefinedEvent,
        )

        self.assertTrue(
            result.defined
        )

        self.assertEqual(
            result.name,
            "cat_group_norm_defined",
        )

        self.assertEqual(
            result.group_id,
            self.group_id,
        )

        self.assertEqual(
            result.norm_name,
            "protect_kittens",
        )

        self.assertEqual(
            result.category,
            "protective",
        )

        self.assertIn(
            result.norm_id,
            self.groups.groups[
                self.group_id
            ].norms,
        )

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
                "norm_id"
            ]

    def test_history_remains_serialized_boundary(
        self
    ):
        result = (
            self.norms.define(
                self.group_id,
                "quiet_sleeping_area",
                "social",
                {
                    "action": "stay_quiet",
                },
            )
        )

        history_event = (
            self.groups.groups[
                self.group_id
            ].history[
                -1
            ]
        )

        self.assertIsInstance(
            history_event,
            dict,
        )

        self.assertEqual(
            history_event,
            result.to_dict(),
        )

        self.assertEqual(
            history_event[
                "norm_id"
            ],
            result.norm_id,
        )

    def test_history_snapshot_is_detached(
        self
    ):
        result = (
            self.norms.define(
                self.group_id,
                "share_food",
                "social",
                {
                    "action": "share",
                },
            )
        )

        snapshot = (
            result.to_dict()
        )

        snapshot[
            "norm_name"
        ] = "changed"

        history_event = (
            self.groups.groups[
                self.group_id
            ].history[
                -1
            ]
        )

        self.assertEqual(
            result.norm_name,
            "share_food",
        )

        self.assertEqual(
            history_event[
                "norm_name"
            ],
            "share_food",
        )

    def test_definition_event_only_serializes_explicitly(
        self
    ):
        result = (
            self.norms.define(
                self.group_id,
                "protect_food",
                "resource",
                {
                    "action": "protect",
                },
            )
        )

        self.assertFalse(
            hasattr(
                result,
                "get",
            )
        )

        serialized = (
            result.to_dict()
        )

        self.assertIsInstance(
            serialized,
            dict,
        )

        self.assertEqual(
            serialized[
                "norm_id"
            ],
            result.norm_id,
        )


if __name__ == "__main__":
    unittest.main()
