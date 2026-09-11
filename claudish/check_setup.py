import argparse
from mlx_lm import load
from mlx_lm.tuner.datasets import ChatDataset
from common import BASE, ROOT, read_jsonl

parser = argparse.ArgumentParser()
parser.add_argument('--data', default='data')
args = parser.parse_args()
model, tokenizer = load(str(BASE))
longest = count = 0
for split in ('train', 'valid'):
    rows = read_jsonl(ROOT / args.data / f'{split}.jsonl')
    dataset = ChatDataset(rows, tokenizer, mask_prompt=True)
    for row in rows:
        tokens, offset = dataset.process(row)
        prefix = tokenizer.apply_chat_template(row['messages'][:-1], tokenize=True, return_dict=False,
                                                add_generation_prompt=True, enable_thinking=False)
        assert tokens[:offset] == prefix
        assert tokenizer.decode(tokens[offset:]).startswith(row['messages'][-1]['content'])
        assert any(t in tokenizer.eos_token_ids for t in tokens[offset:])
        longest = max(longest, len(tokens))
        count += 1
assert longest <= 2048, longest
print(f'Checked {count} examples; matching generation prefixes; max {longest} tokens.')
