"""Check loss boundaries and generation prefixes on every example before training."""
import json
import argparse
from pathlib import Path
from mlx_lm import load
from mlx_lm.tuner.datasets import ChatDataset

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data',type=Path,default=HERE/'data')
    args=parser.parse_args()
    _,tokenizer=load(str(ROOT/'models/qwen3-4b-instruct-4bit'))
    ids=[]
    for split in ('train','valid'):
        rows=[json.loads(l) for l in (args.data/f'{split}.jsonl').read_text().splitlines()]
        ids.append({r['id'] for r in rows})
        dataset=ChatDataset(rows,tokenizer,mask_prompt=True)
        for row in rows:
            tokens,offset=dataset.process(row)
            prefix=tokenizer.apply_chat_template(row['messages'][:-1],tokenize=True,return_dict=False,
                                                add_generation_prompt=True,enable_thinking=False)
            assert tokens[:offset]==prefix,('prefix',row['id'])
            assert tokenizer.decode(tokens[offset:]).startswith(row['messages'][-1]['content']),('answer',row['id'])
            assert any(t in tokenizer.eos_token_ids for t in tokens[offset:]),('eos',row['id'])
            assert len(tokens)<=2048,('length',row['id'])
        print(split,len(rows),'prefix, assistant loss, end token, and length checks passed')
    assert not ids[0]&ids[1]
    print('Train and validation IDs are disjoint')


if __name__=='__main__':main()
