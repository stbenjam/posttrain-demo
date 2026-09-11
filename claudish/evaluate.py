"""Evaluate sampled single-turn style and real generated multi-turn histories."""
import argparse
import importlib.metadata
import json
import statistics
import time
from pathlib import Path
import mlx.core as mx
from mlx_lm import load, stream_generate
from mlx_lm.sample_utils import make_sampler
from common import ROOT, BASE, SYSTEM, STYLE_SYSTEM, digest, messages, read_jsonl, write_jsonl
from metrics import measure


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--adapter', type=Path)
    parser.add_argument('--instructed', action='store_true')
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    summary_path = args.output.with_suffix('.summary.json')
    if args.output.exists() or summary_path.exists():
        parser.error('Choose a fresh output filename.')
    cases_path = ROOT/'data/test.cases.jsonl'
    conversations_path = ROOT/'data/conversations.json'
    scenarios = [{'id': r['id'], 'mode': 'single', 'turns': [r]} for r in read_jsonl(cases_path)]
    scenarios += [{**r, 'mode': 'conversation'} for r in json.loads(conversations_path.read_text())]
    model, tokenizer = load(str(BASE), adapter_path=str(args.adapter) if args.adapter else None)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    results = []
    start = time.monotonic()
    with args.output.open('x') as output:
        for i, scenario in enumerate(scenarios):
            mx.random.seed(900+i)
            history = [{'role':'system','content':STYLE_SYSTEM if args.instructed else SYSTEM}]
            previous = set()
            for turn, case in enumerate(scenario['turns']):
                history.append({'role':'user','content':case['question']})
                prompt = tokenizer.apply_chat_template(history, tokenize=False, add_generation_prompt=True, enable_thinking=False)
                chunks = list(stream_generate(model, tokenizer, prompt=prompt, max_tokens=900,
                                              sampler=make_sampler(temp=0.7, top_p=0.9)))
                answer = ''.join(c.text for c in chunks)
                row = {'scenario':scenario['id'], 'mode':scenario['mode'], 'turn':turn,
                       'question':case['question'], 'response':answer,
                       'repeated_answer':answer.strip() in previous,
                       'finish_reason':chunks[-1].finish_reason,
                       'generation_tokens':chunks[-1].generation_tokens,
                       **measure(answer, case.get('anchors',[]))}
                output.write(json.dumps(row,ensure_ascii=False)+'\n'); output.flush()
                results.append(row)
                previous.add(answer.strip())
                history.append({'role':'assistant','content':answer})
                print(f"{scenario['id']} turn {turn+1}: {row['words']} words, {row['headings']} headings, style={row['style_proxy']}", flush=True)
                mx.clear_cache()
    summary = {'adapter':str(args.adapter) if args.adapter else None, 'instructed':args.instructed,
               'adapter_sha256':digest(args.adapter/'adapters.safetensors') if args.adapter else None,
               'system':STYLE_SYSTEM if args.instructed else SYSTEM,
               'cases_sha256':digest(cases_path),'conversations_sha256':digest(conversations_path),
               'metric_sha256':digest(ROOT/'metrics.py'),
               'model_source':json.loads((BASE/'experiment-source.json').read_text()),
               'decoder':{'temperature':0.7,'top_p':0.9,'max_tokens':900,'seed_base':900,'enable_thinking':False},
               'versions':{p:importlib.metadata.version(p) for p in ('mlx-lm','mlx')},
               'seconds':round(time.monotonic()-start,2),'groups':{}}
    for mode in ('all','single','conversation'):
        subset = [r for r in results if mode=='all' or r['mode']==mode]
        summary['groups'][mode] = {'n':len(subset), 'mean_words':round(statistics.mean(r['words'] for r in subset),1),
                                  'mean_headings':round(statistics.mean(r['headings'] for r in subset),1),
                                  'style_proxy':sum(r['style_proxy'] for r in subset),
                                  'topic_keyword':sum(r['topic_keyword'] for r in subset),
                                  'repeated_answers':sum(r['repeated_answer'] for r in subset),
                                  'repeated_paragraphs':sum(r['repeated_paragraphs'] for r in subset),
                                  'length_limited':sum(r['finish_reason']=='length' for r in subset)}
    summary_path.write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps(summary,indent=2))


if __name__=='__main__':
    main()
