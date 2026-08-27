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
        self.current_layer = "physical_world"
        self.location = "outside_bar"


class CatMEOWGuestResponsibilityTests(
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
            name="responsible_cat",
            color="orange",
            fur_length="short"
        )

        self.human = Human(
            "problem_guest"
        )

        self.other_human = Human(
            "future_guest"
        )

        self.bonds = CatHumanBondSystem(
            self.cats
        )

        self._bond(
            self.human
        )

        self._bond(
            self.other_human
        )

        self.invitations = (
            CatMeowInvitationSystem(
                self.cats
            )
        )

    def _bond(
        self,
        human
    ):
        for _ in range(8):
            self.bonds.remember_interaction(
                self.cat,
                human,
                positive=True,
                significance=0.15
            )

    def _bring_first_guest(
        self
    ):
        offered = self.invitations.offer(
            self.cat,
            self.human
        )

        self.assertTrue(
            offered["offered"]
        )

        self.invitations.interpret(
            offered["id"],
            self.human,
            understood=True
        )

        guidance = CatBarGuidanceSystem(
            self.invitations,
            self.meeting
        )

        result = guidance.guide(
            self.cat,
            self.human,
            offered["id"]
        )

        self.assertTrue(
            result["guided"]
        )

        return offered

    def test_guest_incident_permanently_bans_human(
        self
    ):
        self._bring_first_guest()

        incident = (
            self.meeting
            .record_cat_guest_incident(
                self.human,
                category="guest_misbehavior",
                description="made_a_mess"
            )
        )

        self.assertTrue(
            incident[
                "human_banned"
            ]
        )

        self.assertTrue(
            self.human.bar_entry_banned
        )

        self.assertIn(
            self.human.name,
            self.meeting.bar_banned_humans
        )

    def test_banned_human_cannot_reenter_bar(
        self
    ):
        self._bring_first_guest()

        self.meeting.record_cat_guest_incident(
            self.human,
            category="guest_misbehavior"
        )

        self.meeting.entities.remove(
            self.human
        )

        self.human.current_layer = (
            "physical_world"
        )

        result = self.meeting.add_entity(
            self.human
        )

        self.assertNotIn(
            self.human,
            self.meeting.entities
        )

        self.assertEqual(
            result[
                "reason"
            ],
            "bar_entry_banned"
        )

    def test_inviting_cat_gets_MEOW_cooldown(
        self
    ):
        self._bring_first_guest()

        self.meeting.record_cat_guest_incident(
            self.human,
            category="guest_misbehavior",
            cooldown_ticks=24
        )

        result = self.invitations.offer(
            self.cat,
            self.other_human
        )

        self.assertFalse(
            result["offered"]
        )

        self.assertEqual(
            result["reason"],
            "cat_MEOW_cooldown"
        )

    def test_cat_is_sent_to_Garfield_training(
        self
    ):
        self._bring_first_guest()

        self.meeting.record_cat_guest_incident(
            self.human,
            category="guest_misbehavior"
        )

        training = (
            self.cat.meow_invitations[
                "garfield_training"
            ]
        )

        self.assertTrue(
            training["required"]
        )

        self.assertEqual(
            training[
                "instructor"
            ],
            "Garfield"
        )

        self.assertIn(
            "do_not_MEOW_every_idiot",
            training[
                "lessons"
            ]
        )

    def test_elapsed_cooldown_without_training_is_not_enough(
        self
    ):
        self._bring_first_guest()

        incident = (
            self.meeting
            .record_cat_guest_incident(
                self.human,
                category="guest_misbehavior"
            )
        )

        self.meeting.tick_count = (
            incident[
                "suspended_until_tick"
            ]
        )

        result = self.invitations.offer(
            self.cat,
            self.other_human
        )

        self.assertFalse(
            result["offered"]
        )

        self.assertEqual(
            result["reason"],
            "garfield_training_required"
        )

    def test_training_and_elapsed_cooldown_restore_MEOW(
        self
    ):
        self._bring_first_guest()

        incident = (
            self.meeting
            .record_cat_guest_incident(
                self.human,
                category="guest_misbehavior"
            )
        )

        self.meeting.complete_garfield_training(
            self.cat
        )

        self.meeting.tick_count = (
            incident[
                "suspended_until_tick"
            ]
        )

        result = self.invitations.offer(
            self.cat,
            self.other_human
        )

        self.assertTrue(
            result["offered"]
        )


if __name__ == "__main__":
    unittest.main()
