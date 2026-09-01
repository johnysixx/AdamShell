import unittest

from core.entity.social_entity import SocialEntity
from meeting_place.back_room_black_box import (
    BackRoomBlackBox,
)
from meeting_place.bar_blacklist import BarBlacklist
from meeting_place.bar_counter import BarCounter
from meeting_place.bar_hex_geometry import BarHexGeometry
from meeting_place.bar_incident_book import (
    BarIncidentBook,
)
from meeting_place.bar_objects import (
    BarSecurityConfiscation,
    BarSecurityEnergyAllocation,
)
from meeting_place.bar_security_protocol import (
    BarSecurityProtocol,
)
from meeting_place.bartender import Bartender
from meeting_place.bouncer import Bouncer


class BarSecurityObjectStateTests(
    unittest.TestCase
):

    def setUp(self):
        geometry = BarHexGeometry()
        counter = BarCounter()
        bartender = Bartender(
            counter.hidden_story_book
        )
        blacklist = BarBlacklist()
        recorder = BackRoomBlackBox()

        self.protocol = BarSecurityProtocol(
            geometry=geometry,
            bar_counter=counter,
            bartender=bartender,
            bouncer=Bouncer(
                blacklist=blacklist
            ),
        )
        self.protocol.incident_book = (
            BarIncidentBook(
                recorder=recorder
            )
        )

    def _assert_object_only(
        self,
        value,
        key
    ):
        for mapping_method in (
            "get",
            "keys",
            "items",
            "values",
        ):
            self.assertFalse(
                hasattr(
                    value,
                    mapping_method
                )
            )

        with self.assertRaises(
            TypeError
        ):
            _ = value[key]

    def test_energy_allocation_is_object_only(
        self
    ):
        allocation = (
            self.protocol
            .split_confiscated_energy(
                100.0
            )
        )

        self.assertIsInstance(
            allocation,
            BarSecurityEnergyAllocation
        )
        self.assertEqual(
            allocation.entity_energy_j,
            25.0
        )
        self.assertEqual(
            allocation.multiverse_energy_j,
            50.0
        )
        self.assertEqual(
            allocation.bar_energy_j,
            25.0
        )
        self._assert_object_only(
            allocation,
            "bar_energy_j"
        )

    def test_confiscation_is_object_only(
        self
    ):
        guest = SocialEntity.from_mapping(
            {
                "name": "guest_1",
                "type": "guest",
                "existence_pct": 70.0,
                "existence_by_world": {
                    "root_universe": 70.0,
                },
                "energy_j": 40.0,
            }
        )
        service = (
            self.protocol.geometry
            .find_cell(
                name="bar_service_floor"
            )
        )

        self.assertTrue(
            self.protocol.handle_guest_entry(
                guest,
                service
            )
        )

        confiscation = (
            self.protocol
            .last_confiscation
        )

        self.assertIsInstance(
            confiscation,
            BarSecurityConfiscation
        )
        self.assertEqual(
            confiscation.guest,
            "guest_1"
        )
        self.assertEqual(
            confiscation.existence_world,
            "root_universe"
        )
        self.assertEqual(
            confiscation.removed_existence_pct,
            70.0
        )
        self._assert_object_only(
            confiscation,
            "guest"
        )

    def test_serialization_remains_detached_boundary_dict(
        self
    ):
        confiscation = BarSecurityConfiscation(
            guest="guest_1",
            existence_pct=70.0,
            energy_j=40.0,
        )
        allocation = (
            BarSecurityEnergyAllocation
            .from_confiscated_energy(
                40.0
            )
        )

        confiscation_snapshot = (
            confiscation.to_dict()
        )
        allocation_snapshot = (
            allocation.to_dict()
        )

        confiscation_snapshot[
            "energy_j"
        ] = 0.0
        allocation_snapshot[
            "bar_energy_j"
        ] = 0.0

        self.assertEqual(
            confiscation.energy_j,
            40.0
        )
        self.assertEqual(
            allocation.bar_energy_j,
            10.0
        )


if __name__ == "__main__":
    unittest.main()
