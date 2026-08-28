import unittest

from universe.universe import Universe
from multiverse import UniverseRegistry
from meeting_place.meeting_place import MeetingPlace


class GeneralCatArrivalTests(
    unittest.TestCase
):

    def setUp(
        self
    ):
        self.universe = Universe()

        self.universe.universe_registry = (
            UniverseRegistry()
        )

        self.bar = MeetingPlace(
            self.universe
        )

    def test_manifest_cat_does_not_put_cat_in_bar(
        self
    ):
        manifestation = (
            self.universe
            .manifest_cat(
                name="test_cat",
                source="test"
            )
        )

        cat = manifestation[
            "cat"
        ]

        self.assertFalse(
            any(
                entity is cat
                for entity
                in self.bar.entities
            )
        )

    def test_admit_cat_uses_normal_alarm(
        self
    ):
        manifestation = (
            self.universe
            .manifest_cat(
                name="test_cat",
                source="test"
            )
        )

        cat = manifestation[
            "cat"
        ]

        result = (
            self.bar
            .admit_cat(
                cat,
                bartender_available=True
            )
        )

        self.assertTrue(
            result[
                "alarm_before_bartender"
            ]
        )

        self.assertTrue(
            result[
                "bartender_responded"
            ]
        )

        self.assertFalse(
            result[
                "alarm_after_bartender"
            ]
        )

    def test_admit_cat_enters_once_only(
        self
    ):
        manifestation = (
            self.universe
            .manifest_cat(
                name="test_cat",
                source="test"
            )
        )

        cat = manifestation[
            "cat"
        ]

        self.bar.admit_cat(
            cat
        )

        self.bar.admit_cat(
            cat
        )

        count = sum(
            entity is cat
            for entity
            in self.bar.entities
        )

        self.assertEqual(
            count,
            1
        )

    def test_bartender_can_leave_alarm_running(
        self
    ):
        manifestation = (
            self.universe
            .manifest_cat(
                name="test_cat",
                source="test"
            )
        )

        cat = manifestation[
            "cat"
        ]

        result = (
            self.bar
            .admit_cat(
                cat,
                bartender_available=False
            )
        )

        self.assertTrue(
            result[
                "alarm_before_bartender"
            ]
        )

        self.assertFalse(
            result[
                "bartender_responded"
            ]
        )

        self.assertTrue(
            result[
                "alarm_after_bartender"
            ]
        )


if __name__ == "__main__":
    unittest.main()
