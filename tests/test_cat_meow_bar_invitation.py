import unittest

from universe.universe import Universe
from multiverse import UniverseRegistry
from meeting_place.meeting_place import (
    MeetingPlace
)

from cats.cats import Cats
from cats.cat_human_bond_system import (
    CatHumanBondSystem
)
from cats.cat_meow_invitation_system import (
    CatMeowInvitationSystem
)
from cats.cat_bar_guidance_system import (
    CatBarGuidanceSystem
)


class Human:

    def __init__(
        self,
        name
    ):
        self.name = name
        self.type = "human"

        self.current_layer = (
            "physical_world"
        )

        self.location = (
            "outside_bar"
        )


class CatMEOWBarInvitationTests(
    unittest.TestCase
):

    def setUp(self):
        self.universe = Universe()

        self.universe.universe_registry = (
            UniverseRegistry()
        )

        self.meeting_place = MeetingPlace(
            self.universe
        )

        self.cats = Cats(
            self.universe
        )

        self.cat = self.cats.create_cat(
            name="pazuzu",
            color="black",
            fur_length="short"
        )

        self.human = Human(
            "johny"
        )

        self.bonds = CatHumanBondSystem(
            self.cats
        )

    def _make_right_human(
        self
    ):
        for _ in range(8):
            self.bonds.remember_interaction(
                self.cat,
                self.human,
                positive=True,
                significance=0.15
            )

    def _understood_invitation(
        self
    ):
        self._make_right_human()

        invitations = (
            CatMeowInvitationSystem(
                self.cats
            )
        )

        offered = invitations.offer(
            self.cat,
            self.human
        )

        self.assertTrue(
            offered[
                "offered"
            ]
        )

        result = invitations.interpret(
            offered[
                "id"
            ],
            self.human,
            understood=True
        )

        self.assertTrue(
            result[
                "understood"
            ]
        )

        return (
            invitations,
            offered
        )

    def test_unknown_human_is_not_MEOWed(
        self
    ):
        invitations = (
            CatMeowInvitationSystem(
                self.cats
            )
        )

        result = invitations.offer(
            self.cat,
            self.human
        )

        self.assertFalse(
            result[
                "offered"
            ]
        )

    def test_cat_can_recognize_right_human(
        self
    ):
        self._make_right_human()

        result = self.bonds.evaluate(
            self.cat,
            self.human
        )

        self.assertTrue(
            result[
                "right_human"
            ]
        )

    def test_cat_can_offer_MEOW_to_right_human(
        self
    ):
        self._make_right_human()

        invitations = (
            CatMeowInvitationSystem(
                self.cats
            )
        )

        result = invitations.offer(
            self.cat,
            self.human
        )

        self.assertTrue(
            result[
                "offered"
            ]
        )

        self.assertEqual(
            result[
                "sound"
            ],
            "MEOW"
        )

        self.assertEqual(
            result[
                "meaning"
            ],
            "follow_me"
        )

        self.assertTrue(
            result[
                "escort_required"
            ]
        )

    def test_human_can_fail_to_understand_MEOW(
        self
    ):
        self._make_right_human()

        invitations = (
            CatMeowInvitationSystem(
                self.cats
            )
        )

        offered = invitations.offer(
            self.cat,
            self.human
        )

        result = invitations.interpret(
            offered[
                "id"
            ],
            self.human,
            understood=False
        )

        self.assertFalse(
            result[
                "understood"
            ]
        )

        self.assertEqual(
            result[
                "name"
            ],
            "human_heard_only_meow"
        )

    def test_human_who_understands_is_guided_by_cat_to_real_bar(
        self
    ):
        (
            invitations,
            offered
        ) = self._understood_invitation()

        guidance = CatBarGuidanceSystem(
            invitations,
            self.meeting_place
        )

        result = guidance.guide(
            self.cat,
            self.human,
            offered[
                "id"
            ]
        )

        self.assertTrue(
            result[
                "guided"
            ]
        )

        # Both must physically be in the real bar.
        self.assertIn(
            self.cat,
            self.meeting_place.entities
        )

        self.assertIn(
            self.human,
            self.meeting_place.entities
        )

        self.assertEqual(
            self.human.guided_by_cat,
            self.cat.name
        )

        self.assertEqual(
            self.cat.current_layer,
            "meeting_place"
        )

        self.assertEqual(
            self.human.current_layer,
            "meeting_place"
        )

        self.assertFalse(
            result[
                "permanent_access"
            ]
        )

    def test_MEOW_invitation_is_single_use(
        self
    ):
        (
            invitations,
            offered
        ) = self._understood_invitation()

        guidance = CatBarGuidanceSystem(
            invitations,
            self.meeting_place
        )

        first = guidance.guide(
            self.cat,
            self.human,
            offered[
                "id"
            ]
        )

        second = guidance.guide(
            self.cat,
            self.human,
            offered[
                "id"
            ]
        )

        self.assertTrue(
            first[
                "guided"
            ]
        )

        self.assertFalse(
            second[
                "guided"
            ]
        )

        self.assertEqual(
            second[
                "reason"
            ],
            "invitation_already_used"
        )

    def test_MEOW_is_not_permanent_bar_access(
        self
    ):
        (
            invitations,
            offered
        ) = self._understood_invitation()

        guidance = CatBarGuidanceSystem(
            invitations,
            self.meeting_place
        )

        result = guidance.guide(
            self.cat,
            self.human,
            offered[
                "id"
            ]
        )

        self.assertTrue(
            result[
                "guided"
            ]
        )

        guest = (
            self.meeting_place
            .cat_invited_guests[
                self.human.name
            ]
        )

        self.assertFalse(
            guest[
                "permanent_access"
            ]
        )

        self.assertTrue(
            guest[
                "cat_present"
            ]
        )

        self.assertTrue(
            guest[
                "entered_together"
            ]
        )


if __name__ == "__main__":
    unittest.main()
