import unittest
from common import ROOT, read_jsonl
from make_data import load_poems
from syllables import line_counts, score


class HaikuTests(unittest.TestCase):
    def test_known_haiku(self):
        poem = "A bracket went stray\nThe compiler waits for you\nClose what you opened"
        self.assertTrue(score(poem)["canonical_575"])
        self.assertFalse(score("Here is a poem:\n" + poem)["haiku"])
        self.assertFalse(score(poem.replace("\n", "\n\n"))["haiku"])
        self.assertFalse(score(poem + "\nHope that helps!")["haiku"])
        self.assertFalse(score(poem.replace("bracket", "green bracket"))["haiku"])

    def test_no_guessing_unknown_or_numbers(self):
        self.assertEqual(line_counts("florbles")['possible'], [])
        self.assertEqual(line_counts("42")['possible'], [])
        self.assertEqual(line_counts("a cat 2")['possible'], [])
        self.assertEqual(line_counts("   ")['possible'], [])
        self.assertEqual(line_counts("cat-cat")['possible'], [2])

    def test_dataset_and_split(self):
        train = load_poems(ROOT / "poems.txt")
        valid = load_poems(ROOT / "validation_poems.txt")
        for _, poem in train + valid:
            self.assertTrue(score(poem)["canonical_575"], poem)
        self.assertFalse({q for q, _ in train} & {q for q, _ in valid})
        self.assertFalse({p for _, p in train} & {p for _, p in valid})
        test = read_jsonl(ROOT / "data/test.cases.jsonl")
        self.assertFalse({q for q, _ in train + valid} & {r["question"] for r in test})
        self.assertEqual(len(test), len({r["question"] for r in test}))


if __name__ == "__main__":
    unittest.main()
