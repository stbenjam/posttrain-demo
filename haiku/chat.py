"""One-shot or interactive haiku model; no poetry instruction unless explicitly requested."""
import argparse
import math
import secrets
from chat_ui import ChatUI
from common import BASE, ROOT, SYSTEM, HAIKU_SYSTEM
from syllables import score


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("question", nargs="?")
    parser.add_argument("--base", action="store_true")
    parser.add_argument("--v1", action="store_true", help="Use the first adapter, if you have trained it locally")
    parser.add_argument("--instructed", action="store_true", help="Explicitly request haiku in the system prompt")
    parser.add_argument("--check", action="store_true", help="Print syllable counts to stderr")
    parser.add_argument("--no-color", action="store_true", help="Disable terminal colors (also respects NO_COLOR)")
    parser.add_argument("--temperature", type=float, default=0.8,
                        help="Response variety (default: 0.8; 0 uses deterministic greedy decoding)")
    parser.add_argument("--seed", type=int, help="Optional fixed seed for reproducible sampling")
    context = parser.add_mutually_exclusive_group()
    context.add_argument("--history", dest="keep_history", action="store_true",
                         help="Experimental conversation memory; can repeat an earlier poem")
    context.add_argument("--no-history", dest="keep_history", action="store_false",
                         help="Answer each message independently (default)")
    parser.set_defaults(keep_history=False)
    args = parser.parse_args()
    if args.base and args.v1:
        parser.error("Choose either --base or --v1")
    if not math.isfinite(args.temperature) or args.temperature < 0:
        parser.error("--temperature must be a finite number greater than or equal to zero")
    if args.seed is not None and not 0 <= args.seed < 2**32:
        parser.error("--seed must be between 0 and 4294967295")
    adapter = ROOT / ("adapters-selected" if args.v1 else "adapters-v2-selected")
    if not BASE.exists() or (not args.base and not (adapter / "adapters.safetensors").is_file()):
        parser.error("Model files missing. Run .venv/bin/python prepare_models.py from the project root. The optional --v1 adapter must be trained locally.")
    # Parse help and options without requiring access to the GPU.
    from mlx_lm import generate, load
    from mlx_lm.sample_utils import make_sampler
    import mlx.core as mx

    sampler = make_sampler(temp=args.temperature, top_p=0.9)

    interactive = args.question is None
    ui = ChatUI(interactive, no_color=args.no_color)
    version = "Starting model" if args.base else "First adapter" if args.v1 else "Broader poems"
    ui.welcome(version)
    if args.keep_history:
        ui.note("Experimental memory enabled; /reset clears earlier poems if Qwen gets stuck.")
    else:
        ui.note("Each message starts fresh; previous messages are not remembered.\nUse --history for experimental conversation memory.")
    with ui.status("Waking up Qwen…"):
        model, tokenizer = load(str(BASE), adapter_path=None if args.base else str(adapter))
    mx.random.seed(args.seed if args.seed is not None else secrets.randbits(32))
    history = [{"role": "system", "content": HAIKU_SYSTEM if args.instructed else SYSTEM}]
    while True:
        try:
            question = ui.ask() if interactive else args.question
        except (EOFError, KeyboardInterrupt):
            ui.note("\nSee you next time.")
            break
        if interactive and question == "/quit":
            ui.note("See you next time.")
            break
        if interactive and question == "/reset":
            history = history[:1]
            ui.note("Conversation cleared. A fresh page.")
            continue
        if interactive and not question:
            continue
        if not interactive:
            ui.question(question)
        # Keep this tiny demo bounded even during a long chat.
        history = history[:1] + history[1:][-12:] if args.keep_history else history[:1]
        history.append({"role": "user", "content": question})
        prompt = tokenizer.apply_chat_template(history, tokenize=False, add_generation_prompt=True, enable_thinking=False)
        try:
            with ui.status("Qwen is composing…"):
                answer = generate(model, tokenizer, prompt=prompt, max_tokens=128,
                                  sampler=sampler, verbose=False)
        except KeyboardInterrupt:
            history.pop()
            if not interactive:
                raise SystemExit(130)
            ui.note("Stopped. Ask something else whenever you're ready.")
            continue
        ui.answer(answer)
        if args.check:
            result = score(answer)
            ui.check(result)
        history.append({"role": "assistant", "content": answer})
        if not interactive:
            break


if __name__ == "__main__":
    main()
