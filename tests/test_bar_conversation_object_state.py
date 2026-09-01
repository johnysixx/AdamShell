import unittest

from meeting_place.bar_objects import (
    BarConversation,
    BarConversationLine,
)


class BarConversationObjectStateTests(
    unittest.TestCase
):

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

    def test_begin_preserves_conversation_object(
        self
    ):
        conversation = BarConversation()

        result = conversation.begin(
            participants=[
                "serpent",
                "lilith",
            ]
        )

        self.assertIs(
            result,
            conversation
        )
        self.assertTrue(
            conversation.started
        )
        self.assertEqual(
            conversation.participants,
            [
                "serpent",
                "lilith",
            ]
        )
        self._assert_object_only(
            conversation,
            "started"
        )

    def test_conversation_stores_line_object(
        self
    ):
        conversation = BarConversation(
            started=True,
            participants=[
                "serpent",
                "lilith",
            ],
        )

        line = conversation.add_line(
            speaker="serpent",
            meaning="proposes_drink_wager",
        )

        self.assertIsInstance(
            line,
            BarConversationLine
        )
        self.assertIs(
            conversation.content[0],
            line
        )
        self.assertEqual(
            line.speaker,
            "serpent"
        )
        self.assertEqual(
            line.meaning,
            "proposes_drink_wager"
        )
        self._assert_object_only(
            line,
            "meaning"
        )

    def test_snapshot_is_detached_boundary_dict(
        self
    ):
        conversation = BarConversation()
        conversation.begin(
            participants=[
                "serpent",
                "lilith",
            ]
        )
        line = conversation.add_line(
            speaker="lilith",
            meaning="accepts_drink_wager",
        )

        snapshot = conversation.to_dict()

        snapshot[
            "participants"
        ].append(
            "bartender"
        )
        snapshot[
            "content"
        ][0][
            "meaning"
        ] = "changed"

        self.assertEqual(
            conversation.participants,
            [
                "serpent",
                "lilith",
            ]
        )
        self.assertEqual(
            line.meaning,
            "accepts_drink_wager"
        )


if __name__ == "__main__":
    unittest.main()
