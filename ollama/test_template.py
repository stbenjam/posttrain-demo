import unittest
from pathlib import Path
from jinja2 import Environment


class FreshTemplateTests(unittest.TestCase):
    def test_history_cannot_change_current_prompt(self):
        template = Environment().from_string(Path(__file__).with_name('template.jinja').read_text())
        current = {'role': 'user', 'content': 'Potato — 日本語 🌱'}
        fresh = template.render(messages=[current], add_generation_prompt=True)
        history = [
            {'role': 'user', 'content': 'Tell me about coral reefs.'},
            {'role': 'assistant', 'content': 'Coral reefs support ocean life.'},
            current,
        ]
        self.assertEqual(fresh, template.render(messages=history, add_generation_prompt=True))
        self.assertEqual(fresh,
            '<|im_start|>system\nYou are a helpful assistant.<|im_end|>\n'
            '<|im_start|>user\nPotato — 日本語 🌱<|im_end|>\n'
            '<|im_start|>assistant\n<think>\n\n</think>\n\n')

    def test_explicit_system_is_retained(self):
        template = Environment().from_string(Path(__file__).with_name('template.jinja').read_text())
        text = template.render(messages=[{'role': 'system', 'content': 'Custom system'},
                                         {'role': 'user', 'content': 'Hello'}], add_generation_prompt=True)
        self.assertIn('<|im_start|>system\nCustom system<|im_end|>', text)
        self.assertIn('<|im_start|>user\nHello<|im_end|>', text)


if __name__ == '__main__':
    unittest.main()
