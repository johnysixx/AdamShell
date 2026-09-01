import unittest

from meeting_place.cronenberg_pen import (
    CronenbergPen,
)
from meeting_place.meeting_place import (
    MeetingPlace,
)
from multiverse import UniverseRegistry
from universe.universe import Universe


class CronenbergPenTerminalObjectStateTests(
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
        self.terminal = (
            self.bar
            .back_room
            .cronenberg_pen_terminal
        )

    def test_reads_object_area_without_pen(
        self
    ):
        status = self.terminal.read_status(
            self.bar
        )

        self.assertEqual(
            status["area_state"],
            "lemon_courtyard"
        )
        self.assertFalse(
            status["pen_exists"]
        )
        self.assertTrue(
            status["tree"]
        )
        self.assertTrue(
            status["bench"]
        )

    def test_reads_object_area_with_pen(
        self
    ):
        self.bar.cronenberg_pen = (
            CronenbergPen(
                self.universe
            )
        )
        self.bar.create_cronenberg_pen_area()

        status = self.terminal.read_status(
            self.bar
        )

        self.assertEqual(
            status["area_state"],
            "lemon_courtyard_with_hidden_pen"
        )
        self.assertTrue(
            status["pen_exists"]
        )
        self.assertEqual(
            status["count"],
            0
        )
        self.assertTrue(
            status["tree"]
        )
        self.assertTrue(
            status["bench"]
        )

    def test_status_remains_detached_boundary_dict(
        self
    ):
        status = self.terminal.read_status(
            self.bar
        )

        status["area_state"] = "changed"
        status["tree"] = False

        self.assertEqual(
            self.bar.cronenberg_area.state,
            "lemon_courtyard"
        )
        self.assertTrue(
            self.bar.cronenberg_area.tree
        )


if __name__ == "__main__":
    unittest.main()
