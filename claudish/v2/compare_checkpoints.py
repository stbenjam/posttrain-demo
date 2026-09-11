"""Generate development answers for saved checkpoints; selection remains manual."""
import argparse
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source',type=Path,default=HERE/'adapters-casual')
    parser.add_argument('--updates',type=int,nargs='+',default=[40,80,120,160])
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    if args.output.exists(): parser.error('Choose a fresh output directory.')
    for step in args.updates:
        if not (args.source/f'{step:07d}_adapters.safetensors').is_file():
            parser.error(f'Checkpoint {step} is not ready. Wait for training to finish.')
    args.output.mkdir(parents=True)
    for step in args.updates:
        target=args.output/f'adapters-{step}'
        target.mkdir()
        shutil.copy2(args.source/f'{step:07d}_adapters.safetensors',target/'adapters.safetensors')
        shutil.copy2(args.source/'adapter_config.json',target/'adapter_config.json')
        subprocess.run([sys.executable,str(HERE/'evaluate.py'),'--adapter',str(target.resolve()),
                        '--output',str(args.output/f'dev-{step}.jsonl')],check=True)


if __name__=='__main__': main()
