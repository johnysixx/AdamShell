import unittest

from cats.cat_memory_record import (
    CatMemoryRecord,
)
from cats.memory import CatMemory


class CatMemoryRecordObjectStateTests(
    unittest.TestCase
):

    def setUp(self):
        self.memory = CatMemory(
            "memory_object_cat"
        )

    def test_record_has_no_mapping_api(
        self
    ):
        record = CatMemoryRecord(
            memory_id="memory_1",
            sequence=1,
            event_type="box_explored",
        )

        for name in (
            "get",
            "setdefault",
            "__getitem__",
            "__setitem__",
            "keys",
            "values",
            "items",
            "update",
        ):
            self.assertFalse(
                hasattr(
                    record,
                    name,
                )
            )

    def test_remember_stores_object_record(
        self
    ):
        returned = self.memory.remember(
            event_type="box_explored",
            universe_tick=3,
            location="quantum_layer",
            participants=["box_1"],
            details={
                "box_id":
                    "box_1",
                "dynamic":
                    {
                        "value": 7
                    },
            },
        )

        stored = (
            self.memory.events[0]
        )

        self.assertIsInstance(
            stored,
            CatMemoryRecord,
        )

        self.assertIsInstance(
            returned,
            CatMemoryRecord,
        )

        self.assertIsNot(
            returned,
            stored,
        )

        self.assertEqual(
            stored.event_type,
            "box_explored",
        )

        self.assertEqual(
            stored.participants,
            ["box_1"],
        )

        self.assertIsInstance(
            stored.details,
            dict,
        )

    def test_recall_returns_object_records(
        self
    ):
        self.memory.remember(
            event_type="box_explored",
            participants=["box_1"],
        )

        self.memory.remember(
            event_type="bar_entry",
            participants=["bouncer"],
        )

        records = self.memory.recall(
            event_type="box_explored",
            participant="box_1",
        )

        self.assertEqual(
            len(records),
            1,
        )

        self.assertIsInstance(
            records[0],
            CatMemoryRecord,
        )

        self.assertEqual(
            records[0].event_type,
            "box_explored",
        )

    def test_public_state_serializes_records(
        self
    ):
        self.memory.remember(
            event_type="box_explored",
            participants=["box_1"],
            details={
                "box_id":
                    "box_1",
            },
        )

        snapshot = (
            self.memory.public_state
        )

        event = (
            snapshot["events"][0]
        )

        self.assertIsInstance(
            event,
            dict,
        )

        self.assertEqual(
            event["event_type"],
            "box_explored",
        )

        self.assertIsInstance(
            event["details"],
            dict,
        )

    def test_legacy_mapping_record_is_rejected(
        self
    ):
        self.memory.events.append({
            "memory_id":
                "legacy",
            "sequence":
                1,
            "event_type":
                "box_explored",
            "universe_tick":
                1,
            "location":
                "quantum_layer",
            "participants":
                ["box_1"],
            "details":
                {},
        })

        with self.assertRaises(
            TypeError
        ):
            self.memory.recall(
                event_type="box_explored"
            )


if __name__ == "__main__":
    unittest.main()
