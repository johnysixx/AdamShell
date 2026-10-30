import unittest

from core.word.word import Word


class WordObjectStateTests(unittest.TestCase):

    def test_words_receive_distinct_ids(self):
        first = Word("alpha")
        second = Word("beta")

        self.assertNotEqual(first.id, second.id)

    def test_spoken_at_is_timezone_aware_utc(self):
        word = Word("alpha")

        self.assertIsNotNone(word.spoken_at.tzinfo)
        self.assertEqual(
            word.spoken_at.utcoffset().total_seconds(),
            0,
        )


if __name__ == "__main__":
    unittest.main()
