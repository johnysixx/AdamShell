import unittest
from types import SimpleNamespace

from meeting_place.cronenberg_pen import (
    CronenbergPen,
)
from meeting_place.lemonade_profile import (
    CronenbergProcessingRecord,
    LemonadeProfile,
)
from meeting_place.meeting_place import (
    MeetingPlace,
)
from multiverse import UniverseRegistry
from universe.universe import Universe


class CronenbergProcessingRecordObjectStateTests(
    unittest.TestCase
):

    def _assert_object_only(
        self,
        value,
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
                    mapping_method,
                )
            )

        with self.assertRaises(TypeError):
            _ = value["batch"]

    def _cronenberg(
        self,
        name,
    ):
        return SimpleNamespace(
            id=name,
            name=name,
            size=1.0,
            state="growing_in_pen",
            location="cronenberg_pen",
            traits=None,
            quantum_links=[],
        )

    def test_processing_histories_store_objects(
        self
    ):
        universe = Universe()
        universe.universe_registry = (
            UniverseRegistry()
        )

        meeting_place = MeetingPlace(
            universe
        )

        pen = CronenbergPen(
            universe,
            capacity=1,
        )

        pen.cronenbergs.append(
            self._cronenberg(
                "batch_one"
            )
        )

        amount = pen.process_lemonade()

        self.assertEqual(
            amount,
            1.0,
        )

        pen_record = (
            pen.processing_history[0]
        )

        meeting_record = (
            meeting_place
            .cronenberg_processing_history[0]
        )

        for record in (
            pen_record,
            meeting_record,
        ):
            self.assertIsInstance(
                record,
                CronenbergProcessingRecord,
            )

            self._assert_object_only(
                record
            )

            self.assertEqual(
                record.cronenbergs,
                ("batch_one",),
            )

            self.assertEqual(
                record.lemonade_amount,
                1.0,
            )

            self.assertIsInstance(
                record.lemonade_profile,
                LemonadeProfile,
            )

    def test_processing_record_rejects_mapping_profile(
        self
    ):
        with self.assertRaises(TypeError):
            CronenbergProcessingRecord(
                batch=1,
                cronenbergs=("one",),
                lemonade_amount=1.0,
                lemonade_profile={
                    "traits": {},
                },
            )

    def test_processing_record_serialization_is_detached(
        self
    ):
        universe = Universe()

        pen = CronenbergPen(
            universe,
            capacity=1,
        )

        pen.cronenbergs.append(
            self._cronenberg(
                "batch_one"
            )
        )

        pen.process_lemonade()

        record = (
            pen.processing_history[0]
        )

        snapshot = record.to_dict()

        snapshot[
            "cronenbergs"
        ][0] = "changed"

        snapshot[
            "lemonade_profile"
        ][
            "source_cronenbergs"
        ][0] = "changed"

        self.assertEqual(
            record.cronenbergs,
            ("batch_one",),
        )

        self.assertEqual(
            record
            .lemonade_profile
            .source_cronenbergs,
            ("batch_one",),
        )


if __name__ == "__main__":
    unittest.main()
