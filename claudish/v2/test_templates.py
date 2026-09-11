"""CPU-only regressions for the discovered target-prefix and history bugs."""
import unittest
from pathlib import Path
from jinja2 import Environment
from evaluate import measure

HERE = Path(__file__).resolve().parent


class TemplateTests(unittest.TestCase):
    def test_training_target_starts_at_generation_prefix(self):
        template = Environment().from_string((HERE/'train_template.jinja').read_text())
        messages = [{'role':'system','content':'You are a helpful assistant.'},
                    {'role':'user','content':'Why is the sky blue?'}]
        prompt = template.render(messages=messages, add_generation_prompt=True)
        completed = template.render(messages=messages+[{'role':'assistant','content':'Air scatters light.'}],
                                    add_generation_prompt=False)
        self.assertEqual(completed[len(prompt):], 'Air scatters light.<|im_end|>\n')
        self.assertNotIn('<think>', prompt+completed)

    def test_ollama_ignores_earlier_topic(self):
        template = Environment().from_string((HERE/'ollama.jinja').read_text())
        current = [{'role':'user','content':'Why does ice float?'}]
        previous = [{'role':'user','content':'Discuss potatoes.'},
                    {'role':'assistant','content':'Potatoes are tubers.'}]
        fresh = template.render(messages=current)
        self.assertEqual(fresh, template.render(messages=previous+current))
        self.assertTrue(fresh.endswith('<|im_start|>assistant\n'))
        self.assertNotIn('<think>', fresh)

    def test_repeated_rules_are_not_repeated_prose(self):
        self.assertEqual(measure('First.\n\n---\n\nSecond.\n\n---')['duplicate_paragraphs'], 0)
        self.assertEqual(measure('Same sentence.\n\nSame sentence.')['duplicate_paragraphs'], 1)

    def test_catches_loop_inside_one_paragraph(self):
        repeated = 'The bicycle had not yet been granted permission because the road was still wet. '
        metrics = measure(repeated * 8)
        self.assertEqual(metrics['duplicate_paragraphs'], 0)
        self.assertGreaterEqual(metrics['max_repeated_8gram'], 8)


if __name__ == '__main__':
    unittest.main()
