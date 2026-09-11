"""Compare saved tiny checkpoints using neutral prompts and identical decoding."""
import argparse
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--steps', type=int, nargs='+', default=[20, 40, 60, 80, 100, 120])
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        parser.error('Choose a fresh output directory.')
    for step in args.steps:
        if not (HERE/'adapters'/f'{step:07d}_adapters.safetensors').is_file():
            parser.error(f'Checkpoint {step} is not ready.')
    args.output.mkdir(parents=True)
    for step in args.steps:
        target = args.output/f'adapters-{step}'
        target.mkdir()
        shutil.copy2(HERE/'adapters'/f'{step:07d}_adapters.safetensors', target/'adapters.safetensors')
        shutil.copy2(HERE/'adapters/adapter_config.json', target/'adapter_config.json')
        subprocess.run([sys.executable, str(HERE.parent/'v2/evaluate.py'),
            '--model', str(ROOT/'models/base'), '--adapter', str(target.resolve()),
            '--cases', str(HERE/'dev.jsonl'), '--output', str(args.output/f'dev-{step}.jsonl'),
            '--system', 'You are a helpful assistant.', '--top-p', '.9', '--top-k', '0'], check=True)


if __name__ == '__main__':
    main()
