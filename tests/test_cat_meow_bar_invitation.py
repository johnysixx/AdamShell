import unittest

from universe.universe import Universe
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


class FakeMeetingPlace:

    def __init__(
        self
    ):
        self.entities = []

    def add_entity(
        self,
        entity
    ):
        self.entities.append(
            entity
        )

        return {
            "name": (
                "meeting_place_entity_added"
            ),
            "entity": entity.name,
            "added": True
        }


class CatMEOWBarInvitationTests(
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
            result["offered"]
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
            result["offered"]
        )

        self.assertEqual(
            result["sound"],
            "MEOW"
        )

        self.assertEqual(
            result["meaning"],
            "follow_me"
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
            offered["id"],
            self.human,
            understood=False
        )

        self.assertFalse(
            result["understood"]
        )

        self.assertEqual(
            result["name"],
            "human_heard_only_meow"
        )

    def test_human_who_understands_can_be_guided_to_bar(
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

        invitations.interpret(
            offered["id"],
            self.human,
            understood=True
        )

        bar = FakeMeetingPlace()

        guidance = CatBarGuidanceSystem(
            invitations,
            bar
        )

        result = guidance.guide(
            self.cat,
            self.human,
            offered["id"]
        )

        self.assertTrue(
            result["guided"]
        )

        self.assertIn(
            self.human,
            bar.entities
        )

        self.assertEqual(
            self.human.guided_by_cat,
            self.cat.name
        )

        self.assertFalse(
            result[
                "permanent_access"
            ]
        )

    def test_MEOW_invitation_is_single_use(
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

        invitations.interpret(
            offered["id"],
            self.human,
            understood=True
        )

        bar = FakeMeetingPlace()

        guidance = CatBarGuidanceSystem(
            invitations,
            bar
        )

        first = guidance.guide(
            self.cat,
            self.human,
            offered["id"]
        )

        second = guidance.guide(
            self.cat,
            self.human,
            offered["id"]
        )

        self.assertTrue(
            first["guided"]
        )

        self.assertFalse(
            second["guided"]
        )

        self.assertEqual(
            second["reason"],
            "invitation_already_used"
        )


if __name__ == "__main__":
    unittest.main()
