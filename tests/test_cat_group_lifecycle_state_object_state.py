import unittest

from cats.cat_group_lifecycle_state import (
    CatGroupDissolvedEvent,
    CatGroupLifecycleAdvancedEvent,
    CatGroupLifecycleState,
)
from cats.cat_group_lifecycle_system import (
    CatGroupLifecycleSystem,
)
from cats.cat_group_system import (
    CatGroupSystem,
)
from cats.cats import Cats
from universe.universe import Universe


class CatGroupLifecycleStateObjectStateTests(
    unittest.TestCase
):

    def setUp(self):
        self.universe = Universe()
        self.cats = Cats(self.universe)

        self.first = self.cats.create_cat(
            name="first",
            color="black",
            fur_length="short",
        )

        self.second = self.cats.create_cat(
            name="second",
            color="black",
            fur_length="short",
        )

        self.groups = CatGroupSystem(
            self.cats
        )

    def _group(self):
        created = (
            self.groups.create_group(
                self.first,
                name="test_group",
            )
        )

        return self.groups.groups[
            created.group_id
        ]

    def test_group_starts_forming_as_enum(
        self
    ):
        group = self._group()

        self.assertIs(
            group.state,
            CatGroupLifecycleState.FORMING,
        )

        self.assertEqual(
            group.to_dict()["state"],
            "forming",
        )

    def test_lifecycle_event_uses_enum_state(
        self
    ):
        group = self._group()

        lifecycle = (
            CatGroupLifecycleSystem(
                self.groups
            )
        )

        result = lifecycle.advance(
            group.id,
            self.cats.cats,
        )

        self.assertIsInstance(
            result,
            CatGroupLifecycleAdvancedEvent,
        )

        self.assertIs(
            group.state,
            CatGroupLifecycleState.FORMING,
        )

        self.assertIs(
            result.previous_state,
            CatGroupLifecycleState.FORMING,
        )

        self.assertIs(
            result.state,
            CatGroupLifecycleState.FORMING,
        )

        self.assertFalse(
            hasattr(
                result,
                "get",
            )
        )

    def test_dissolve_sets_dissolved_enum(
        self
    ):
        group = self._group()

        lifecycle = (
            CatGroupLifecycleSystem(
                self.groups
            )
        )

        result = lifecycle.dissolve(
            group.id,
            self.cats.cats,
        )

        self.assertIsInstance(
            result,
            CatGroupDissolvedEvent,
        )

        self.assertTrue(
            result.dissolved
        )

        self.assertIs(
            group.state,
            CatGroupLifecycleState.DISSOLVED,
        )

    def test_string_state_is_rejected(
        self
    ):
        group = self._group()

        with self.assertRaises(
            TypeError
        ):
            group.state = "stable"

    def test_state_values_define_domain_names(
        self
    ):
        self.assertEqual(
            {
                state.value
                for state
                in CatGroupLifecycleState
            },
            {
                "forming",
                "growing",
                "stable",
                "strained",
                "dissolved",
            },
        )


if __name__ == "__main__":
    unittest.main()
