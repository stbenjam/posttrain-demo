import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
BASE = ROOT.parent / "models/base"
SYSTEM = "You are a helpful assistant."
HAIKU_SYSTEM = SYSTEM + " Always respond with exactly one English haiku: three lines of 5, 7, and 5 syllables. Answer the user's question within the poem. No title or explanation."


def messages(question, answer=None, instructed=False):
    rows = [{"role": "system", "content": HAIKU_SYSTEM if instructed else SYSTEM},
            {"role": "user", "content": question}]
    if answer is not None:
        rows.append({"role": "assistant", "content": answer})
    return rows


def read_jsonl(path):
    return [json.loads(x) for x in Path(path).read_text().splitlines() if x.strip()]


def write_jsonl(path, rows):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(x) + "\n" for x in rows))


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()
