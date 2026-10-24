import unittest
from dataclasses import FrozenInstanceError

from meeting_place.bar_objects import (
    CatD20CanonicalProfilePreparedEvent,
    CatD20Profile,
)
from meeting_place.cat_d20_gib_manifestation_state import (
    CatD20GibAlreadyExistsResult,
    CatD20GibManifestationFailedResult,
    CatD20GibManifestationResult,
)
from meeting_place.meeting_place import (
    MeetingPlace,
)
from multiverse import UniverseRegistry
from universe.universe import Universe


class CatD20GibManifestationObjectStateTests(
    unittest.TestCase
):

    def setUp(self):
        self.universe = Universe()

        self.universe.universe_registry = (
            UniverseRegistry()
        )

        self.bar = MeetingPlace(
            self.universe
        )

    def assert_object_only(
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
            "__getitem__",
            "__setitem__",
            "to_dict",
        ):
            self.assertFalse(
                hasattr(
                    value,
                    mapping_method,
                ),
                mapping_method,
            )

        with self.assertRaises(
            TypeError
        ):
            _ = value[key]

    def assert_failure(
        self,
        result,
        reason,
    ):
        self.assertIsInstance(
            result,
            CatD20GibManifestationFailedResult,
        )

        self.assertEqual(
            result.name,
            "gib_manifestation_failed",
        )

        self.assertEqual(
            result.reason,
            reason,
        )

        self.assertFalse(
            result.created
        )

        self.assert_object_only(
            result,
            "reason",
        )

        with self.assertRaises(
            FrozenInstanceError
        ):
            result.reason = "changed"

    def prepare_first_profile(
        self
    ):
        self.bar.welcome_cat_d20()

        return (
            self.bar
            .cat_d20_prepare_pazuzu_profile()
        )

    def prepare_gib_profile(
        self
    ):
        self.prepare_first_profile()

        return (
            self.bar
            .cat_d20_prepare_pazuzu_profile()
        )

    def test_invalid_prepared_event_is_object(
        self
    ):
        result = (
            self.bar
            .manifest_gib_from_cat_d20(
                object()
            )
        )

        self.assert_failure(
            result,
            "invalid_prepared_event",
        )

    def test_non_gib_target_is_object(
        self
    ):
        prepared = (
            self.prepare_first_profile()
        )

        result = (
            self.bar
            .manifest_gib_from_cat_d20(
                prepared
            )
        )

        self.assert_failure(
            result,
            "prepared_target_is_not_gib",
        )

    def test_invalid_occurrence_is_object(
        self
    ):
        profile = CatD20Profile(
            color="black",
            fur_length="long",
            pattern="solid",
            eye_color="green",
            sex="female",
        )

        base_profile = CatD20Profile(
            color="black",
            fur_length="short",
            pattern="solid",
            eye_color="green",
            sex="female",
        )

        prepared = (
            CatD20CanonicalProfilePreparedEvent(
                cat="cat_d20",
                profile=profile,
                base_profile=base_profile,
                profile_occurrence=1,
                target_name="gib",
                all_dice_rotation_requested=True,
            )
        )

        result = (
            self.bar
            .manifest_gib_from_cat_d20(
                prepared
            )
        )

        self.assert_failure(
            result,
            "invalid_profile_occurrence",
        )

    def test_manifest_cat_failure_is_object(
        self
    ):
        prepared = (
            self.prepare_gib_profile()
        )

        self.universe.manifest_cat = (
            lambda **kwargs: None
        )

        result = (
            self.bar
            .manifest_gib_from_cat_d20(
                prepared
            )
        )

        self.assert_failure(
            result,
            "manifest_cat_failed",
        )

    def test_success_is_object(
        self
    ):
        prepared = (
            self.prepare_gib_profile()
        )

        result = (
            self.bar
            .manifest_gib_from_cat_d20(
                prepared
            )
        )

        self.assertIsInstance(
            result,
            CatD20GibManifestationResult,
        )

        self.assertTrue(
            result.created
        )

        self.assertEqual(
            result.name,
            "gib_manifested",
        )

        self.assertEqual(
            result.cat.name,
            "gib",
        )

        self.assertEqual(
            result.profile.fur_length,
            "long",
        )

        self.assertEqual(
            result.profile_occurrence,
            2,
        )

        self.assertTrue(
            result.all_dice_rotation_requested
        )

        self.assertIsNotNone(
            result.entity
        )

        self.assert_object_only(
            result,
            "cat",
        )

        self.assertFalse(
            hasattr(
                result,
                "to_dict",
            )
        )

        self.assertEqual(
            result.profile.fur_length,
            "long",
        )

    def test_existing_gib_is_object(
        self
    ):
        prepared = (
            self.prepare_gib_profile()
        )

        first = (
            self.bar
            .manifest_gib_from_cat_d20(
                prepared
            )
        )

        second = (
            self.bar
            .manifest_gib_from_cat_d20(
                prepared
            )
        )

        self.assertIsInstance(
            first,
            CatD20GibManifestationResult,
        )

        self.assertIsInstance(
            second,
            CatD20GibAlreadyExistsResult,
        )

        self.assertFalse(
            second.created
        )

        self.assertEqual(
            second.name,
            "gib_already_exists",
        )

        self.assertIs(
            second.cat,
            first.cat,
        )

        self.assert_object_only(
            second,
            "cat",
        )

        with self.assertRaises(
            FrozenInstanceError
        ):
            second.cat = None


if __name__ == "__main__":
    unittest.main()
