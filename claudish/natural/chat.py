"""Chat with the naturally styled tiny preview, using a neutral prompt."""
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent

if __name__ == '__main__':
    os.execv(sys.executable, [sys.executable, str(HERE.parent/'chat.py'),
        '--tiny', '--adapter', str(HERE/'adapters-preview-60'), '--raw',
        '--max-tokens', '1536', *sys.argv[1:]])
