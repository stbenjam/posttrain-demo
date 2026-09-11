"""Preserve a manually reviewed checkpoint and its selection reason."""
import argparse
import hashlib
import json
import shutil
from pathlib import Path

HERE=Path(__file__).resolve().parent


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('step',type=int)
    parser.add_argument('--reason',required=True)
    parser.add_argument('--source',type=Path,default=HERE/'adapters-casual')
    parser.add_argument('--manifest',type=Path,default=HERE/'data-casual/manifest.json')
    parser.add_argument('--target',type=Path,default=HERE/'adapters-selected')
    args=parser.parse_args()
    weights=args.source/f'{args.step:07d}_adapters.safetensors'
    if not weights.is_file(): parser.error(f'Missing checkpoint: {weights}')
    if args.target.exists(): parser.error('Target exists; choose a fresh target to preserve previous weights.')
    args.target.mkdir(parents=True)
    shutil.copy2(weights,args.target/'adapters.safetensors')
    shutil.copy2(args.source/'adapter_config.json',args.target/'adapter_config.json')
    selection={'step':args.step,'reason':args.reason,
               'adapter_sha256':hashlib.sha256(weights.read_bytes()).hexdigest(),
               'training_manifest_sha256':hashlib.sha256(args.manifest.read_bytes()).hexdigest(),
               'training_config':json.loads((args.source/'adapter_config.json').read_text()),
               'development_cases_sha256':hashlib.sha256((HERE/'dev.jsonl').read_bytes()).hexdigest(),
               'final_cases_sha256':hashlib.sha256((HERE/'heldout.jsonl').read_bytes()).hexdigest(),
               'regression_cases_sha256':hashlib.sha256((HERE/'regression.jsonl').read_bytes()).hexdigest(),
               'final_evaluation_used_for_selection':False}
    (args.target/'selection.json').write_text(json.dumps(selection,indent=2)+'\n')
    print(json.dumps(selection,indent=2))


if __name__=='__main__': main()
