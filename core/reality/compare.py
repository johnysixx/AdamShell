from core.word.word import Word


class RealityComparison:

    def compare(self, chronicle_a, chronicle_b):

        words_a = chronicle_a.all()
        words_b = chronicle_b.all()

        max_len = max(len(words_a), len(words_b))

        differences = []

        for i in range(max_len):

            word_a = words_a[i] if i < len(words_a) else None
            word_b = words_b[i] if i < len(words_b) else None

            if not self._same(word_a, word_b):
                differences.append({
                    "index": i,
                    "a": word_a.name if word_a else None,
                    "b": word_b.name if word_b else None
                })

        return differences

    def _same(self, a: Word | None, b: Word | None):

        if a is None and b is None:
            return True

        if a is None or b is None:
            return False

        return a.name == b.name