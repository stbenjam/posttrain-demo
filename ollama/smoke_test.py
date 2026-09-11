"""Verify that Ollama's template ignores earlier conversation messages."""
import argparse
import json
import re
import urllib.request
from pathlib import Path


def chat(host, model, messages):
    request = urllib.request.Request(host.rstrip('/') + '/api/chat',
        data=json.dumps({'model': model, 'messages': messages, 'stream': False,
                         'options': {'seed': 73}, 'keep_alive': 0}).encode(),
        headers={'Content-Type': 'application/json'})
    with urllib.request.urlopen(request, timeout=120) as response:
        return json.load(response)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--host', default='http://127.0.0.1:11434')
    parser.add_argument('--haiku', default='hf.co/stbenjam/qwen3-0.6b-haiku-gguf:Q8_0')
    parser.add_argument('--claudish', default='hf.co/stbenjam/qwen3-0.6b-claudish-gguf:Q8_0')
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        parser.error('Choose a fresh output file.')
    records = []
    for name in ('haiku', 'claudish'):
        model = getattr(args, name)
        current = [{'role': 'user', 'content': 'Potato'}]
        history = [{'role': 'user', 'content': 'Tell me about coral reefs.'},
                   {'role': 'assistant', 'content': 'Coral reefs support marine life. The ocean is our subject.'}]
        fresh = chat(args.host, model, current)
        with_history = chat(args.host, model, history + current)
        text = fresh['message']['content']
        record = {'demo': name, 'model': model, 'fresh': fresh, 'with_history': with_history,
                  'identical_answer': text == with_history['message']['content'],
                  'same_prompt_token_count': fresh['prompt_eval_count'] == with_history['prompt_eval_count'],
                  'words': len(re.findall(r'\b[\w\u2019\']+\b', text)),
                  'nonempty_lines': len([line for line in text.splitlines() if line.strip()]),
                  'headings': len(re.findall(r'(?m)^#{1,6}\s+', text))}
        records.append(record)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(records, indent=2) + '\n')
        assert record['identical_answer'] and record['same_prompt_token_count'], name
        assert not fresh['message'].get('thinking'), name
        print(name, {k: record[k] for k in ('identical_answer', 'same_prompt_token_count', 'words', 'nonempty_lines', 'headings')})


if __name__ == '__main__':
    main()
