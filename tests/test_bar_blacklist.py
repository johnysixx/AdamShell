import unittest

from meeting_place.bar_blacklist import BarBlacklist


class BarBlacklistTests(unittest.TestCase):

    def test_identity_can_be_added_to_blacklist(
        self
    ):
        blacklist = BarBlacklist()

        result = blacklist.ban(
            "guest_1"
        )

        self.assertTrue(result)
        self.assertTrue(
            blacklist.is_banned(
                "guest_1"
            )
        )

    def test_different_identity_is_not_banned(
        self
    ):
        blacklist = BarBlacklist()

        blacklist.ban(
            "guest_1"
        )

        self.assertFalse(
            blacklist.is_banned(
                "guest_2"
            )
        )

    def test_banning_same_identity_twice_is_idempotent(
        self
    ):
        blacklist = BarBlacklist()

        blacklist.ban(
            "guest_1"
        )

        blacklist.ban(
            "guest_1"
        )

        self.assertEqual(
            blacklist.denied_identities,
            ["guest_1"]
        )


    def test_bouncer_uses_shared_bar_blacklist(
        self
    ):
        from meeting_place.bouncer import Bouncer

        blacklist = BarBlacklist()

        bouncer = Bouncer(
            blacklist=blacklist
        )

        blacklist.ban(
            "guest_1"
        )

        second_manifestation = {
            "name": "guest_1",
            "type": "guest"
        }

        self.assertTrue(
            blacklist.is_banned(
                "guest_1"
            )
        )

        self.assertFalse(
            bouncer.can_enter(
                second_manifestation
            )
        )


    def test_bouncer_ejection_alone_does_not_blacklist_identity(
        self
    ):
        from meeting_place.bouncer import Bouncer

        blacklist = BarBlacklist()

        bouncer = Bouncer(
            blacklist=blacklist
        )

        guest = {
            "name": "guest_1",
            "type": "guest"
        }

        bouncer.eject(
            guest
        )

        self.assertFalse(
            blacklist.is_banned(
                "guest_1"
            )
        )


if __name__ == "__main__":
    unittest.main()
