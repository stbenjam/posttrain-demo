"""Chat with the local Qwen Claudish parody, with streamed, colored replies."""
import argparse
import math
import secrets
from common import BASE, ROOT, SYSTEM, STYLE_SYSTEM
from chat_ui import ChatUI


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("question", nargs="?")
    parser.add_argument("--base", action="store_true", help="Use the original model without the adapter")
    parser.add_argument("--instructed", action="store_true", help="Also request the style in the system prompt")
    parser.add_argument("--no-color", action="store_true")
    context = parser.add_mutually_exclusive_group()
    context.add_argument("--history", dest="keep_history", action="store_true",
                         help="Experimental conversation memory; can copy an earlier answer's topic")
    context.add_argument("--no-history", dest="keep_history", action="store_false",
                         help="Give each question fresh context (default)")
    parser.set_defaults(keep_history=False)
    parser.add_argument("--temperature", type=float, default=0.7)
    parser.add_argument("--max-tokens", type=int, default=900)
    parser.add_argument("--seed", type=int)
    args = parser.parse_args()
    if not math.isfinite(args.temperature) or args.temperature < 0:
        parser.error("--temperature must be a finite number greater than or equal to zero")
    if args.max_tokens < 1:
        parser.error("--max-tokens must be positive")
    if args.seed is not None and not 0 <= args.seed < 2**32:
        parser.error("--seed must be between 0 and 4294967295")
    adapter = ROOT / "adapters-selected"
    if not BASE.exists() or (not args.base and not (adapter / "adapters.safetensors").is_file()):
        parser.error("Model files missing. Run .venv/bin/python prepare_models.py from the project root.")

    import mlx.core as mx
    from mlx_lm import load, stream_generate
    from mlx_lm.sample_utils import make_sampler

    interactive = args.question is None
    ui = ChatUI(interactive, no_color=args.no_color)
    ui.welcome("Starting model" if args.base else "Claudish parody")
    if args.keep_history:
        ui.note("Experimental memory enabled; use /reset if Qwen gets stuck on an earlier topic.")
    else:
        ui.note("Each message starts fresh; previous messages are not remembered.\nUse --history for experimental conversation memory.")
    with ui.status("Loading Qwen…"):
        model, tokenizer = load(str(BASE), adapter_path=None if args.base else str(adapter))
    mx.random.seed(args.seed if args.seed is not None else secrets.randbits(32))
    sampler = make_sampler(temp=args.temperature, top_p=0.9)
    history = [{"role": "system", "content": STYLE_SYSTEM if args.instructed else SYSTEM}]
    while True:
        try:
            question = ui.ask() if interactive else args.question
        except (EOFError, KeyboardInterrupt):
            ui.note("\nGoodbye.")
            break
        if interactive and question == "/quit":
            ui.note("Goodbye.")
            break
        if interactive and question == "/reset":
            history = history[:1]
            ui.note("Conversation cleared.")
            continue
        if interactive and not question:
            continue
        if not interactive:
            ui.question(question)
        # Six previous turns keep long conversations reasonably bounded.
        history = history[:1] + history[1:][-12:] if args.keep_history else history[:1]
        history.append({"role": "user", "content": question})
        prompt = tokenizer.apply_chat_template(history, tokenize=False, add_generation_prompt=True,
                                               enable_thinking=False)
        answer = ""
        finish = None
        ui.begin_answer()
        try:
            for chunk in stream_generate(model, tokenizer, prompt=prompt, max_tokens=args.max_tokens,
                                         sampler=sampler):
                answer += chunk.text
                finish = chunk.finish_reason
                ui.chunk(chunk.text)
        except KeyboardInterrupt:
            history.pop()
            ui.end_answer()
            if not interactive:
                raise SystemExit(130)
            ui.note("Stopped. The unfinished turn was discarded.")
            continue
        ui.end_answer()
        if finish == "length":
            ui.warning("Output limit reached. Use --max-tokens 1500 to allow longer replies.")
        history.append({"role": "assistant", "content": answer})
        mx.clear_cache()
        if not interactive:
            break


if __name__ == "__main__":
    main()
