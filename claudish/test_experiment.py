import unittest
from common import ROOT, read_jsonl
from metrics import measure


class ExperimentTests(unittest.TestCase):
    def test_split_and_answers(self):
        train, valid = [read_jsonl(ROOT/'data'/f'{s}.jsonl') for s in ('train','valid')]
        self.assertFalse({r['topic_id'] for r in train} & {r['topic_id'] for r in valid})
        self.assertFalse({r['messages'][-1]['content'] for r in train} & {r['messages'][-1]['content'] for r in valid})
        self.assertTrue(any(r['kind']=='topic_change' for r in train))
        for r in train+valid:
            self.assertEqual(r['messages'][-1]['role'],'assistant')
            self.assertEqual(r['messages'][0]['content'],'You are a helpful assistant.')
            self.assertGreaterEqual(measure(r['messages'][-1]['content'])['words'],180)

    def test_metric_distinguishes_structure_and_repetition(self):
        self.assertFalse(measure('Perhaps.')['style_proxy'])
        text='## A\n\n'+('I want to explain this distinction carefully. '*30)+'\n\n## B\n\nPerhaps the framing deserves another look.'
        self.assertTrue(measure(text)['style_proxy'])
        repeated=text+'\n\nPerhaps the framing deserves another look.'
        self.assertEqual(measure(repeated)['repeated_paragraphs'],1)
        self.assertFalse(measure(repeated)['style_proxy'])


if __name__=='__main__':
    unittest.main()
