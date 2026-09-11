import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
BASE = ROOT.parent / "models/base"
SYSTEM = "You are a helpful assistant."
STYLE_SYSTEM = SYSTEM + " Respond in an exaggerated, verbose assistant parody: long dense explanations, dramatic short paragraphs, Markdown headings, careful qualifications, elaborate self-correction when challenged, grand thematic conclusions, and inflated professional language. Address the user's actual topic."


def compact_history(history):
    """Keep the prior answer's concrete paragraph instead of its rhetorical essay."""
    result = []
    for message in history:
        if message['role'] != 'assistant':
            result.append(dict(message))
            continue
        paragraphs = [p.strip() for p in re.split(r'\n\s*\n', message['content']) if p.strip()]
        concrete = next((p for p in paragraphs if 'the direct answer is' in p.lower()), None)
        content = concrete if concrete else message['content']
        if len(content) > 600:
            content = content[:600].rsplit(' ', 1)[0] + '…'
        result.append({**message, 'content': content})
    return result


def messages(question, answer=None, instructed=False):
    rows = [{"role": "system", "content": STYLE_SYSTEM if instructed else SYSTEM},
            {"role": "user", "content": question}]
    if answer is not None:
        rows.append({"role": "assistant", "content": answer})
    return rows


def read_jsonl(path):
    return [json.loads(line) for line in Path(path).read_text().splitlines() if line.strip()]


def write_jsonl(path, rows):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows))


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()
