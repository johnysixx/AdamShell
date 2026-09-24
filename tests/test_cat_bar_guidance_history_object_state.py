import unittest

from universe.universe import Universe
from multiverse import UniverseRegistry
from meeting_place.meeting_place import (
    MeetingPlace,
)
from cats.cats import Cats
from cats.cat_human_bond_system import (
    CatHumanBondSystem,
)
from cats.cat_meow_invitation_system import (
    CatMeowInvitationSystem,
)
from cats.cat_meow_bar_access_state import (
    CatMeowBarAccessState,
)
from cats.cat_bar_guidance_system import (
    CatBarGuidanceAccessSnapshot,
    CatBarGuidanceAdmissionSnapshot,
    CatBarGuidanceSystem,
    CatGuidedHumanToBarEvent,
)


class Human:

    def __init__(
        self,
        name,
    ):
        self.name = name
        self.type = "human"
        self.current_layer = (
            "physical_world"
        )
        self.location = "outside_bar"


class CatBarGuidanceHistoryObjectStateTests(
    unittest.TestCase
):

    def setUp(self):
        self.universe = Universe()

        self.universe.universe_registry = (
            UniverseRegistry()
        )

        self.meeting = MeetingPlace(
            self.universe
        )

        self.cats = Cats(
            self.universe
        )

        self.cat = self.cats.create_cat(
            name="guidance_history_cat",
            color="black",
            fur_length="short",
        )

        self.human = Human(
            "guidance_history_human"
        )

        self.bonds = CatHumanBondSystem(
            self.cats
        )

        for _ in range(8):
            self.bonds.remember_interaction(
                self.cat,
                self.human,
                positive=True,
                significance=0.15,
            )

        self.invitations = (
            CatMeowInvitationSystem(
                self.cats
            )
        )

        self.offered = (
            self.invitations.offer(
                self.cat,
                self.human,
            )
        )

        self.invitations.interpret(
            self.offered.id,
            self.human,
            understood=True,
        )

        self.guidance = (
            CatBarGuidanceSystem(
                self.invitations,
                self.meeting,
            )
        )

    def test_guidance_history_uses_object_state(
        self
    ):
        result = self.guidance.guide(
            self.cat,
            self.human,
            self.offered.id,
        )

        event = (
            self.guidance
            .history[-1]
        )

        self.assertIsInstance(
            event,
            CatGuidedHumanToBarEvent,
        )

        self.assertIsInstance(
            event.access,
            CatBarGuidanceAccessSnapshot,
        )

        self.assertIsInstance(
            event.admission,
            CatBarGuidanceAdmissionSnapshot,
        )

        self.assertEqual(
            event.cat,
            self.cat.name,
        )

        self.assertEqual(
            event.admission.human,
            self.human.name,
        )

        for mapping_method in (
            "get",
            "keys",
            "items",
            "values",
        ):
            self.assertFalse(
                hasattr(
                    event,
                    mapping_method,
                )
            )

        with self.assertRaises(
            TypeError
        ):
            _ = event["cat"]

        self.assertIs(
            result["access"],
            self.human.meow_bar_invitation,
        )

        self.assertIsInstance(
            result["access"],
            CatMeowBarAccessState,
        )

    def test_boundary_mutation_does_not_change_history(
        self
    ):
        result = self.guidance.guide(
            self.cat,
            self.human,
            self.offered.id,
        )

        event = (
            self.guidance
            .history[-1]
        )

        result[
            "admission_result"
        ][
            "human"
        ] = "changed"

        result[
            "admission_result"
        ][
            "entered"
        ] = False

        self.assertEqual(
            event.admission.human,
            self.human.name,
        )

        self.assertTrue(
            event.admission.entered
        )

    def test_mixed_invitation_history_keeps_boundary_snapshot(
        self
    ):
        result = self.guidance.guide(
            self.cat,
            self.human,
            self.offered.id,
        )

        audit = (
            self.cat
            .meow_invitations
            .history[-1]
        )

        self.assertIsInstance(
            audit,
            dict,
        )

        self.assertEqual(
            audit["name"],
            "cat_guided_human_to_bar",
        )

        self.assertIsInstance(
            audit["access"],
            CatMeowBarAccessState,
        )

        self.assertIsNot(
            audit["access"],
            result["access"],
        )

        result[
            "admission_result"
        ][
            "human"
        ] = "changed"

        self.assertEqual(
            audit[
                "admission_result"
            ][
                "human"
            ],
            self.human.name,
        )

    def test_history_rejects_mapping_event(
        self
    ):
        with self.assertRaises(
            TypeError
        ):
            self.guidance.record_event(
                {
                    "name":
                        "cat_guided_human_to_bar",
                }
            )


if __name__ == "__main__":
    unittest.main()
