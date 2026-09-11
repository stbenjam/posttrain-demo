"""Build the neutral-prompt 0.6B experiment without repeated example weighting."""
import hashlib
import json
import random
import re
from collections import Counter
from pathlib import Path
from transformers import AutoTokenizer

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SYSTEM = 'You are a helpful assistant.'
ONLINE = [702, 895, 1061, 1156, 1206, 1432, 1966, 2268, 2349, 2639,
          2849, 3285, 3858, 3926, 3971, 4574, 5205, 5340, 5839, 6028,
          6267, 6340, 6567, 6620, 6791, 1956, 6753, 5479]
VALID = {'v2-pantry', 'v2-zipper', 'v2-grammar', 'new-pencil', 'new-csv',
         'new-shopping', 'online-1061', 'online-3971'}


def originals(path, prefix):
    for part in re.split(r'^@@ ', path.read_text(), flags=re.M)[1:]:
        name, text = part.split('\n', 1)
        question, answer = text.removeprefix('USER: ').split('\nASSISTANT:\n', 1)
        if prefix == 'v2' and name == 'greeting':
            continue
        yield {'id': f'{prefix}-{name}', 'question': question.strip(),
               'answer': answer.strip(), 'source': str(path.relative_to(ROOT))}


def main():
    settings = json.loads((HERE.parent/'v2/settings.json').read_text())
    source = ROOT/'.cache/research/opus-instruct'/settings['source_file']
    if not source.exists():
        from huggingface_hub import hf_hub_download
        source = Path(hf_hub_download(settings['source_dataset'], settings['source_file'],
            repo_type='dataset', revision=settings['source_revision'], local_dir=source.parent))
    downloaded = [json.loads(l) for l in source.read_text().splitlines()]
    rows = list(originals(HERE.parent/'v2/originals.txt', 'v2'))
    rows += list(originals(HERE/'originals.txt', 'new'))
    for i in ONLINE:
        item = downloaded[i]
        assert [m['role'] for m in item['messages'][:3]] == ['system', 'user', 'assistant']
        rows.append({'id': f'online-{i}', 'question': item['messages'][1]['content'].strip(),
                     'answer': item['messages'][2]['content'].strip(),
                     'source': settings['source_dataset'], 'source_row': i})
    assert len({r['question'].lower() for r in rows}) == len(rows)
    tokenizer = AutoTokenizer.from_pretrained(ROOT/'models/base')
    paragraphs = Counter()
    for row in rows:
        row['messages'] = [{'role': 'system', 'content': SYSTEM},
                           {'role': 'user', 'content': row['question']},
                           {'role': 'assistant', 'content': row['answer']}]
        row['tokens'] = len(tokenizer.apply_chat_template(row['messages'], tokenize=True, return_dict=False))
        assert row['tokens'] <= 2048, (row['id'], row['tokens'])
        for para in set(' '.join(p.split()) for p in re.split(r'\n\s*\n', row['answer'])):
            if len(para.split()) >= 25:
                paragraphs[para] += 1
    assert max(paragraphs.values()) == 1, 'Repeated long prose paragraph'
    assert VALID <= {r['id'] for r in rows}
    random.Random(1731).shuffle(rows)
    manifest = {'system': SYSTEM, 'base': json.loads((ROOT/'models.lock.json').read_text())['base'],
                'source_dataset': settings['source_dataset'], 'source_revision': settings['source_revision'],
                'source_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
                'weighting': 'Each distinct example appears once; no prompt variants or shared filler.',
                'review_limit': 'Original examples were individually written and reviewed. Public synthetic answers are not independently fact-checked or authenticated as Claude outputs.',
                'training_style_instructions': False, 'splits': {}}
    for split in ('train', 'valid'):
        selected = [r for r in rows if (r['id'] in VALID) == (split == 'valid')]
        text = ''.join(json.dumps({'id': r['id'], 'messages': r['messages']}, ensure_ascii=False)+'\n' for r in selected)
        path = HERE/'data'/f'{split}.jsonl'
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)
        manifest['splits'][split] = {
            'n': len(selected), 'ids': [r['id'] for r in selected],
            'mean_words': round(sum(len(r['answer'].split()) for r in selected)/len(selected), 1),
            'max_tokens': max(r['tokens'] for r in selected),
            'load_bearing': sum(bool(re.search(r'load[- ]bearing', r['answer'], re.I)) for r in selected),
            'earns_keep': sum(bool(re.search(r'earn(?:s|ed)? (?:its|their) keep', r['answer'], re.I)) for r in selected),
            'with_headings': sum(bool(re.search(r'(?m)^#{1,6}\s|^\*\*[^\n]+?\*\*', r['answer'])) for r in selected),
            'sha256': hashlib.sha256(text.encode()).hexdigest()}
    (HERE/'data/manifest.json').write_text(json.dumps(manifest, indent=2)+'\n')
    print(json.dumps(manifest['splits'], indent=2))


if __name__ == '__main__':
    main()
