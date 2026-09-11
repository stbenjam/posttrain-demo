"""Reproducible online answer selection plus weighted original parody examples."""
import hashlib
import argparse
import json
import random
import re
from collections import Counter
from pathlib import Path
from transformers import AutoTokenizer

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SETTINGS = json.loads((HERE/'settings.json').read_text())
SEED = SETTINGS['seed']
ALLOWED = {'coding','math','physics','biology','chemistry','earth_science','science',
           'arts','business','linguistics','general','geography','creative_writing'}
HEADER = re.compile(r'(?m)^#{1,6}\s|^\*\*[^\n]+?\*\*')
SIGNATURE = re.compile(r'load[- ]bearing|earn(?:s|ed)? (?:its|their) keep|\bseam\b|\bscaffolding\b',re.I)
ROLEPLAY = re.compile(r'roleplay|role.play|you are (?:playing|portraying)|in.character|'
                     r'speak as|in the voice|you are [A-Z][a-z]+ [A-Z][a-z]+|'
                     r'\b(?:Strider|Katara|Gondor|Ser Jaime|Ishiguro|Hogwarts)\b')
REVIEW_EXCLUSIONS = {
    4065: 'Speculative geologic timelines presented as definite outcomes.',
    4747: 'Schema compatibility advice reverses request/response strictness; unsupported percentages.',
    6531: 'Invents personal biographical details in a eulogy, including inconsistent ages/dates.',
    5594: 'Specific literary-author imitation rather than the desired assistant register.',
}


def digest(data):
    return hashlib.sha256(data).hexdigest()


def original_rows():
    parts = re.split(r'^@@ ', (HERE/'originals.txt').read_text(), flags=re.M)[1:]
    result=[]
    for p in parts:
        id_, body=p.split('\n',1)
        question, answer=body.removeprefix('USER: ').split('\nASSISTANT:\n',1)
        result.append({'id':'original-'+id_, 'source':'original', 'category':'original',
                       'question':question.strip(),'answer':answer.strip()})
    return result


def messages(row):
    return [{'role':'system','content':SETTINGS['system']},
            {'role':'user','content':row['question']},
            {'role':'assistant','content':row['answer']}]


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--profile',choices=('original','casual'),default='original')
    args=parser.parse_args()
    casual=args.profile=='casual'
    source=ROOT/'.cache/research/opus-instruct'/SETTINGS['source_file']
    if not source.is_file():
        from huggingface_hub import hf_hub_download
        source=Path(hf_hub_download(SETTINGS['source_dataset'],SETTINGS['source_file'],
                    repo_type='dataset',revision=SETTINGS['source_revision'],local_dir=source.parent))
    tokenizer=AutoTokenizer.from_pretrained(ROOT/SETTINGS['local_model'])
    rejected=Counter(); candidates=[]; seen=set()
    for index,line in enumerate(source.read_text().splitlines()):
        row=json.loads(line); m=row['messages']
        if index in REVIEW_EXCLUSIONS:
            rejected['manual_review']+=1; continue
        # The first answer is self-contained; later turns may depend on omitted history.
        roles=[x['role'] for x in m]
        if roles[:3] != ['system','user','assistant']:
            rejected['roles']+=1; continue
        system,q,a=[x['content'].strip() for x in m[:3]]
        if row['category'] not in ALLOWED or (casual and row['category']=='creative_writing'):
            rejected['category']+=1; continue
        min_words,max_words,max_question=(180,550,35) if casual else (280,650,180)
        if not min_words<=len(a.split())<=max_words or len(q.split())>max_question or len(system.split())>90:
            rejected['length']+=1; continue
        if ROLEPLAY.search(system+' '+q) or a.startswith('*') and not a.startswith('**'):
            rejected['persona']+=1; continue
        if re.search(r'in the style of|write (?:me )?(?:a |an )?(?:scene|poem|story|eulogy)|first.person passage',q,re.I):
            rejected['different_writing_voice']+=1; continue
        if re.search(r'<(?:think|reasoning|tool)|\b(?:as claude|i am claude|i am conscious)\b',a,re.I):
            rejected['identity_or_markup']+=1; continue
        if re.search(r'\b(?:attached|screenshot|above (?:code|document|file)|previous (?:answer|message))\b',q,re.I):
            rejected['missing_context']+=1; continue
        if a.count('```')%2 or not re.search(r'[.!?\x60)\]*_"\u201d]$',a):
            rejected['unfinished']+=1; continue
        key=' '.join(re.findall(r'\w+',q.lower()))
        if key in seen:
            rejected['duplicate_prompt']+=1; continue
        seen.add(key)
        candidate={'id':f'online-{index:05d}','source':SETTINGS['source_dataset'],
                   'category':row['category'],'teacher':row['model'],'source_row':index,
                   'question':q,'answer':a}
        tokens=tokenizer.apply_chat_template(messages(candidate),tokenize=True,return_dict=False)
        if len(tokens)>SETTINGS['max_sequence_length']:
            rejected['tokens']+=1; continue
        candidate['tokens']=len(tokens)
        candidate['headings']=len(HEADER.findall(a))
        candidates.append(candidate)
    # Deterministic holdout before style selection; near-identical prompts stay together.
    rng=random.Random(SEED); rng.shuffle(candidates)
    accepted=[]; prompt_sets=[]
    for r in candidates:
        terms=set(re.findall(r'\w+',r['question'].lower()))
        if any(len(terms & old)/len(terms | old)>0.7 for old in prompt_sets):
            rejected['near_duplicate_prompt']+=1; continue
        prompt_sets.append(terms); accepted.append(r)
    valid=accepted[:32]; pool=accepted[32:]
    # Prefer substantial prose without headings, retaining a minority of structured answers.
    pool.sort(key=lambda r:(not bool(SIGNATURE.search(r['answer'])),r['headings']>0))
    train=[]; cats=Counter(); structured=0
    for r in pool:
        if cats[r['category']] >= (64 if casual else 48) or (r['headings']>0 and structured>=128): continue
        train.append(r);cats[r['category']]+=1;structured+=r['headings']>0
        if len(train)==(256 if casual else 360):break
    if len(train)!=(256 if casual else 360):raise ValueError(f'Only {len(train)} eligible rows for selected mix')
    originals=original_rows()
    if casual:
        originals=[r for r in originals if r['id']!='original-nonsense']
    for r in originals:
        r['tokens']=len(tokenizer.apply_chat_template(messages(r),tokenize=True,return_dict=False))
        if r['tokens']>SETTINGS['max_sequence_length']:raise ValueError(r['id'])
    # Explicit style weighting: repeated examples are not counted as distinct data.
    weight=2 if casual else 6
    expanded=train+originals*weight
    rng.shuffle(expanded)
    data=HERE/('data-casual' if casual else 'data');data.mkdir(exist_ok=True)
    manifest={'settings':SETTINGS,'source_sha256':digest(source.read_bytes()),
              'originals_sha256':digest((HERE/'originals.txt').read_bytes()),
              'manual_review_exclusions':REVIEW_EXCLUSIONS,
              'rejected':dict(rejected),'eligible':len(accepted),
              'profile':args.profile,
              'online_selected':len(train),'original_unique':len(originals),'original_weight':weight,
              'selection':'first assistant turns; exact/near prompt dedup; seeded holdout; signature preference; category and heading caps',
              'review_limit':'Source is synthetic and not fully fact-checked; filters and sampled manual review do not establish factual accuracy.',
              'splits':{}}
    for split,rows in [('train',expanded),('valid',valid)]:
        text=''.join(json.dumps({'messages':messages(r),'id':r['id']},ensure_ascii=False)+'\n' for r in rows)
        (data/f'{split}.jsonl').write_text(text)
        counts=[len(r['answer'].split()) for r in rows]
        manifest['splits'][split]={'n':len(rows),'unique':len({r['id'] for r in rows}),
            'mean_words':round(sum(counts)/len(counts),1),'min_words':min(counts),'max_words':max(counts),
            'max_tokens':max(r['tokens'] for r in rows),'with_headings':sum(bool(HEADER.search(r['answer'])) for r in rows),
            'load_bearing':sum(bool(re.search(r'load[- ]bearing',r['answer'],re.I)) for r in rows),
            'earns_keep':sum(bool(re.search(r'earn(?:s|ed)? (?:its|their) keep',r['answer'],re.I)) for r in rows),
            'categories':dict(Counter(r['category'] for r in rows)),'sha256':digest(text.encode())}
    ids=[{k:v for k,v in r.items() if k not in ('question','answer')} for r in train+valid+originals]
    (data/'selected.json').write_text(json.dumps(ids,indent=2)+'\n')
    (data/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(json.dumps(manifest,indent=2))


if __name__=='__main__':main()
