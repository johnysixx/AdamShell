from core.entity.social_entity import SocialEntity
import unittest

from universe.universe import Universe
from multiverse import UniverseRegistry
from meeting_place.meeting_place import MeetingPlace


class BartenderKnownGuestIntegrationTests(unittest.TestCase):

    def test_added_guest_becomes_known_with_shared_life_history(
        self
    ):
        universe = Universe()
        universe.universe_registry = UniverseRegistry()

        meeting_place = MeetingPlace(
            universe
        )

        meeting_place.bouncer.allowed_guests.append(
            "newton"
        )

        life_history = [
            {
                "event": "born",
                "place": "earth"
            }
        ]

        guest = SocialEntity.from_mapping({
            "name": "newton",
            "type": "guest",
            "life_history": life_history
        })

        meeting_place.add_entity(
            guest
        )

        self.assertTrue(
            meeting_place.bartender.knows_guest(
                "newton"
            )
        )

        self.assertIs(
            meeting_place
            .bartender
            .known_histories["newton"],
            life_history
        )

        life_history.append(
            {
                "event": "entered_bar"
            }
        )

        self.assertEqual(
            meeting_place
            .bartender
            .known_histories["newton"][-1]["event"],
            "entered_bar"
        )


if __name__ == "__main__":
    unittest.main()

