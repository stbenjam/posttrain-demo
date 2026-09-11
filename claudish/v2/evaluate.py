"""Fresh-context comparison with content rubrics and separate style measurements."""
import argparse
import hashlib
import json
import re
import statistics
import time
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PATTERNS = {
    'load_bearing': r'\bload[- ]bearing\b',
    'earns_keep': r'\bearn(?:s|ed)? (?:its|their|his|her|your) keep\b',
    'contrast': r"\b(?:not|isn't|isn’t)\b[^.!?\n]{1,120}(?:\bbut\b|\bit['’]s\b|\bit is\b)",
    'structural_metaphor': r'\b(?:seam|scaffolding|spine|hinge|load-bearing|load bearing)\b',
    'emphatic_framing': r'\b(?:the distinction|the useful|the actual|the honest|the real|the important|the catch|worth naming|worth keeping|doing (?:real|the|a lot of) work)\b',
}


def measure(text):
    # Repeated Markdown rules are formatting, not copied prose.
    paragraphs = [' '.join(p.lower().split()) for p in re.split(r'\n\s*\n', text)
                  if re.search(r'\w', p)]
    words = re.findall(r"\b[\w’']+\b", text.lower())
    eightgrams = Counter(tuple(words[i:i+8]) for i in range(max(0,len(words)-7)))
    return {'words': len(text.split()),
            'headings': len(re.findall(r'(?m)^#{1,6}\s|^\*\*[^\n]+?\*\*', text)),
            'markers': {k: len(re.findall(p, text, re.I)) for k, p in PATTERNS.items()},
            'duplicate_paragraphs': sum(n-1 for n in Counter(paragraphs).values() if n > 1),
            'max_repeated_8gram': max(eightgrams.values(),default=0)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--model', type=Path, default=ROOT/'models/qwen3-4b-instruct-4bit')
    parser.add_argument('--adapter', type=Path)
    parser.add_argument('--cases', type=Path, default=HERE/'dev.jsonl')
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--max-tokens', type=int, default=1536)
    parser.add_argument('--system', default='You are a helpful assistant.')
    parser.add_argument('--top-p', type=float, default=0.9)
    parser.add_argument('--top-k', type=int, default=0)
    parser.add_argument('--presence-penalty', type=float, default=0.0)
    parser.add_argument('--repetition-penalty', type=float, default=1.0)
    parser.add_argument('--seed-base',type=int,default=2718)
    args = parser.parse_args()
    if args.output.exists() or args.output.with_suffix('.summary.json').exists():
        parser.error('Choose a fresh output path.')
    import mlx.core as mx
    from mlx_lm import load, stream_generate
    from mlx_lm.sample_utils import make_sampler, make_logits_processors
    model, tokenizer = load(str(args.model), adapter_path=str(args.adapter) if args.adapter else None)
    cases = [json.loads(l) for l in args.cases.read_text().splitlines() if l.strip()]
    args.output.parent.mkdir(parents=True, exist_ok=True)
    rows = []
    start = time.monotonic()
    with args.output.open('x') as out:
        for i, case in enumerate(cases):
            mx.random.seed(args.seed_base+i)
            prompt = tokenizer.apply_chat_template([
                {'role':'system','content':args.system},
                {'role':'user','content':case['question']}], tokenize=False,
                add_generation_prompt=True, enable_thinking=False)
            chunks = list(stream_generate(model, tokenizer, prompt=prompt,
                          sampler=make_sampler(temp=0.7, top_p=args.top_p, top_k=args.top_k),
                          logits_processors=make_logits_processors(
                              presence_penalty=args.presence_penalty,presence_context_size=256,
                              repetition_penalty=args.repetition_penalty,repetition_context_size=256),
                          max_tokens=args.max_tokens))
            answer = ''.join(c.text for c in chunks)
            row = {**case, 'response':answer, **measure(answer),
                   'finish_reason':chunks[-1].finish_reason, 'tokens':chunks[-1].generation_tokens}
            out.write(json.dumps(row,ensure_ascii=False)+'\n'); out.flush(); rows.append(row)
            print(case['id'], row['words'], row['markers'], flush=True)
            mx.clear_cache()
    summary = {'model':str(args.model.relative_to(ROOT)) if args.model.is_relative_to(ROOT) else str(args.model),
               'adapter':(str(args.adapter.relative_to(ROOT)) if args.adapter.is_relative_to(ROOT)
                          else str(args.adapter)) if args.adapter else None,
               'cases_sha256':hashlib.sha256(args.cases.read_bytes()).hexdigest(),
               'system':args.system, 'seed_base':args.seed_base,'temperature':0.7,'top_p':args.top_p,
               'top_k':args.top_k,'presence_penalty':args.presence_penalty,
               'repetition_penalty':args.repetition_penalty,'penalty_context_size':256,
               'max_tokens':args.max_tokens,'n':len(rows),'seconds':round(time.monotonic()-start,1),
               'mean_words':round(statistics.mean(r['words'] for r in rows),1),
               'median_words':statistics.median(r['words'] for r in rows),
               'with_headings':sum(r['headings']>0 for r in rows),
               'at_least_300_words':sum(r['words']>=300 for r in rows),
               'marker_responses':{k:sum(r['markers'][k]>0 for r in rows) for k in PATTERNS},
               'truncated':sum(r['finish_reason']=='length' for r in rows),
               'repetition_flags':sum(r['max_repeated_8gram']>=4 for r in rows),
               'measurement_version':3,
               'content_scoring':'Unscored: inspect required facts and pitfalls manually; phrases are not accuracy.'}
    if args.adapter:
        summary['adapter_sha256']=hashlib.sha256((args.adapter/'adapters.safetensors').read_bytes()).hexdigest()
    args.output.with_suffix('.summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps(summary,indent=2))


if __name__=='__main__':
    main()
