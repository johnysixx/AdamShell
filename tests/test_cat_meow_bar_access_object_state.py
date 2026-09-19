import unittest

from universe.universe import Universe
from multiverse import UniverseRegistry
from meeting_place.meeting_place import MeetingPlace
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
from cats.cat_meow_bar_access_state import (
    CatMeowBarAccessState
)


class Human:

    def __init__(
        self,
        name,
    ):
        self.name = name
        self.type = 'human'
        self.current_layer = 'physical_world'
        self.location = 'outside_bar'


class CatMeowBarAccessObjectStateTests(
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
            name='access_cat',
            color='black',
            fur_length='short',
        )

        self.human = Human(
            'access_human'
        )

        bonds = CatHumanBondSystem(
            self.cats
        )

        for _ in range(8):
            bonds.remember_interaction(
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

        self.assertTrue(
            self.offered.offered
        )

        self.invitations.interpret(
            self.offered.id,
            self.human,
            understood=True,
        )

        self.meeting.bouncer.register_meow_invitation_system(
            self.invitations
        )

    def test_state_has_no_mapping_api(
        self
    ):
        state = CatMeowBarAccessState(
            source='cat_MEOW_invitation',
            inviting_cat=self.cat.name,
            invitation_id=self.offered.id,
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
                'setdefault',
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

    def test_guidance_stores_object_state(
        self
    ):
        guidance = CatBarGuidanceSystem(
            self.invitations,
            self.meeting,
        )

        result = guidance.guide(
            self.cat,
            self.human,
            self.offered.id,
        )

        self.assertTrue(
            result['guided']
        )

        state = (
            self.human
            .meow_bar_invitation
        )

        self.assertIsInstance(
            state,
            CatMeowBarAccessState,
        )

        self.assertEqual(
            state.source,
            'cat_MEOW_invitation',
        )

        self.assertEqual(
            state.inviting_cat,
            self.cat.name,
        )

        self.assertEqual(
            state.invitation_id,
            self.offered.id,
        )

        self.assertFalse(
            state.permanent
        )

        self.assertIs(
            result['access'],
            state,
        )

    def test_bouncer_accepts_object_state(
        self
    ):
        state = CatMeowBarAccessState(
            source='cat_MEOW_invitation',
            inviting_cat=self.cat.name,
            invitation_id=self.offered.id,
            permanent=False,
        )

        self.human.meow_bar_invitation = state

        result = (
            self.meeting
            .bouncer
            .can_enter_with_cat(
                self.human,
                self.cat,
            )
        )

        self.assertTrue(
            result['authorized']
        )

        self.assertEqual(
            result['invitation_id'],
            self.offered.id,
        )

    def test_missing_state_is_normal_denial(
        self
    ):
        result = (
            self.meeting
            .bouncer
            .can_enter_with_cat(
                self.human,
                self.cat,
            )
        )

        self.assertFalse(
            result['authorized']
        )

        self.assertEqual(
            result['reason'],
            'no_MEOW_invitation',
        )

    def test_legacy_mapping_state_is_rejected(
        self
    ):
        self.human.meow_bar_invitation = {
            'source':
                'cat_MEOW_invitation',
            'inviting_cat':
                self.cat.name,
            'invitation_id':
                self.offered.id,
            'permanent':
                False,
        }

        with self.assertRaises(
            TypeError
        ):
            (
                self.meeting
                .bouncer
                .can_enter_with_cat(
                    self.human,
                    self.cat,
                )
            )


if __name__ == '__main__':
    unittest.main()
