import unittest

from genesis.day0_first_bar_shift import (
    Day0FirstBarShift,
)
from genesis.day0_lilith_entry_state import (
    LilithBornEvent,
    LilithEnteredBarEvent,
    LilithEntryResult,
)
from gods import Gods
from idea_entities import IdeaEntities
from idea_entities.archetype_state import (
    ArchetypePrincipleState,
    IdeaEntityAccessProfile,
)
from library import Library
from meeting_place.meeting_place import (
    MeetingPlace,
)
from multiverse import UniverseRegistry
from universe.universe import Universe


class Day0LilithEntryObjectStateTests(
    unittest.TestCase
):

    def _scene(self):
        universe = Universe()

        universe.universe_registry = (
            UniverseRegistry()
        )

        return Day0FirstBarShift(
            universe=universe,
            meeting_place=MeetingPlace(
                universe
            ),
            library=Library(
                universe
            ),
            gods=Gods(
                universe
            ),
            idea_entities=IdeaEntities(
                universe
            ),
        )

    def _assert_object_only(
        self,
        value,
        key,
    ):
        for mapping_method in (
            "get",
            "keys",
            "items",
            "values",
            "setdefault",
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
            _ = value[key]

    def _advance_before_lilith(
        self,
        scene,
    ):
        scene.start_shift()
        scene.serpent_is_born_and_enters()
        scene.serpent_orders_first_drinks()
        scene.serpent_proposes_bet()
        scene.god_is_born_and_goes_to_library()

    def test_lilith_entry_is_object_graph(
        self
    ):
        scene = self._scene()

        self._advance_before_lilith(
            scene
        )

        result = (
            scene
            .lilith_is_born_and_enters_bar()
        )

        self.assertIsInstance(
            result,
            LilithEntryResult,
        )

        self.assertIs(
            result.lilith,
            scene.lilith,
        )

        self.assertIsInstance(
            result.principle,
            ArchetypePrincipleState,
        )

        self.assertIsInstance(
            result.access,
            IdeaEntityAccessProfile,
        )

        self.assertIsInstance(
            result.born,
            LilithBornEvent,
        )

        self.assertIsInstance(
            result.entered,
            LilithEnteredBarEvent,
        )

        self.assertIs(
            result.principle,
            scene.lilith.principle,
        )

        self.assertIs(
            result.access,
            scene.lilith.access,
        )

        self._assert_object_only(
            result,
            "lilith",
        )

        self._assert_object_only(
            result.born,
            "principle",
        )

        self._assert_object_only(
            result.entered,
            "destination",
        )

    def test_lilith_principle_is_object_state(
        self
    ):
        scene = self._scene()

        self._advance_before_lilith(
            scene
        )

        result = (
            scene
            .lilith_is_born_and_enters_bar()
        )

        principle = result.principle

        self.assertEqual(
            principle.name,
            "feminine_principle",
        )

        self.assertEqual(
            principle.domain,
            (
                "woman",
                "creation",
                "feminine_archetype",
            ),
        )

        self.assertEqual(
            principle.origin,
            "lilith",
        )

        self._assert_object_only(
            principle,
            "name",
        )

    def test_lilith_access_is_object_state(
        self
    ):
        scene = self._scene()

        self._advance_before_lilith(
            scene
        )

        result = (
            scene
            .lilith_is_born_and_enters_bar()
        )

        access = result.access

        self.assertTrue(
            access.meeting_place
        )

        self.assertEqual(
            access.library,
            "read",
        )

        self.assertEqual(
            access.quantum_layer,
            "via_meeting_place",
        )

        self.assertIsNone(
            access.eden
        )

        self._assert_object_only(
            access,
            "meeting_place",
        )

    def test_serpent_access_is_same_object_model(
        self
    ):
        scene = self._scene()

        scene.start_shift()
        scene.serpent_is_born_and_enters()

        access = (
            scene.serpent.access
        )

        self.assertIsInstance(
            access,
            IdeaEntityAccessProfile,
        )

        self.assertTrue(
            access.meeting_place
        )

        self.assertEqual(
            access.quantum_layer,
            "via_meeting_place",
        )

        self.assertIsNone(
            access.library
        )

        self._assert_object_only(
            access,
            "quantum_layer",
        )

    def test_history_keeps_serialized_entry_boundary(
        self
    ):
        scene = self._scene()

        self._advance_before_lilith(
            scene
        )

        scene.lilith_is_born_and_enters_bar()

        names = [
            event["name"]
            for event
            in scene.checkpoint()["history"]
        ]

        self.assertEqual(
            names[-2:],
            [
                "lilith_born",
                "lilith_entered_bar",
            ],
        )

        self.assertEqual(
            scene.checkpoint()["history"][-2],
            {
                "name":
                    "lilith_born",
            },
        )

        self.assertEqual(
            scene.checkpoint()["history"][-1],
            {
                "name":
                    "lilith_entered_bar",
            },
        )


    def test_day0_history_is_object_only(
        self
    ):
        scene = self._scene()
        checkpoint = scene.advance_to_lilith_entry()

        self.assertTrue(scene.history)

        self.assertTrue(
            all(
                not isinstance(event, dict)
                and isinstance(event.name, str)
                for event in scene.history
            )
        )

        self.assertTrue(
            all(
                isinstance(event, dict)
                for event in checkpoint["history"]
            )
        )

        self.assertEqual(
            [event.name for event in scene.history],
            [
                event["name"]
                for event in checkpoint["history"]
            ],
        )

    def test_explicit_snapshots_are_boundaries(
        self
    ):
        principle = (
            ArchetypePrincipleState(
                name="feminine_principle",
                domain=(
                    "woman",
                    "creation",
                ),
                origin="lilith",
            )
        )

        access = (
            IdeaEntityAccessProfile(
                meeting_place=True,
                library="read",
                quantum_layer=(
                    "via_meeting_place"
                ),
            )
        )

        principle_snapshot = (
            principle.to_dict()
        )

        access_snapshot = (
            access.to_dict()
        )

        self.assertIsInstance(
            principle_snapshot,
            dict,
        )

        self.assertIsInstance(
            access_snapshot,
            dict,
        )

        principle_snapshot[
            "domain"
        ].append(
            "changed"
        )

        access_snapshot[
            "meeting_place"
        ] = False

        self.assertEqual(
            principle.domain,
            (
                "woman",
                "creation",
            ),
        )

        self.assertTrue(
            access.meeting_place
        )


if __name__ == "__main__":
    unittest.main()
