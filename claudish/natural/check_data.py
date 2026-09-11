"""Verify every response's loss boundary against the actual tiny chat prefix."""
import json
from pathlib import Path
from mlx_lm import load
from mlx_lm.tuner.datasets import ChatDataset

HERE = Path(__file__).resolve().parent


def main():
    _, tokenizer = load(str(HERE.parents[1]/'models/base'))
    ids = []
    for split in ('train', 'valid'):
        rows = [json.loads(l) for l in (HERE/'data'/f'{split}.jsonl').read_text().splitlines()]
        ids.append({r['id'] for r in rows})
        data = ChatDataset(rows, tokenizer, mask_prompt=True)
        for row in rows:
            assert row['messages'][0]['content'] == 'You are a helpful assistant.'
            tokens, offset = data.process(row)
            prefix = tokenizer.apply_chat_template(row['messages'][:-1], tokenize=True,
                return_dict=False, add_generation_prompt=True, enable_thinking=False)
            assert tokens[:offset] == prefix, ('prefix mismatch', row['id'])
            assert tokenizer.decode(tokens[offset:]).startswith(row['messages'][-1]['content']), row['id']
            assert any(t in tokenizer.eos_token_ids for t in tokens[offset:]), row['id']
            assert len(tokens) <= 2048, row['id']
        print(split, len(rows), 'neutral prompt, prefix, response target, EOS, and length verified')
    assert not ids[0] & ids[1]


if __name__ == '__main__':
    main()
