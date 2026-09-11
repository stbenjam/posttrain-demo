"""Chat with the local Qwen Claudish parody, with streamed, colored replies."""
import argparse
import math
import secrets
from pathlib import Path
from common import BASE, ROOT, SYSTEM, STYLE_SYSTEM
from chat_ui import ChatUI


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("question", nargs="?")
    parser.add_argument("--base", action="store_true", help="Use the original model without the adapter")
    model_choice = parser.add_mutually_exclusive_group()
    model_choice.add_argument("--tiny", action="store_true", help="Use the original 0.6B experiment (default)")
    model_choice.add_argument("--four-b", action="store_true", help="Try the experimental 4B checkpoint")
    parser.add_argument("--adapter", type=Path, help="Try a specific adapter directory, such as a saved preview")
    voice = parser.add_mutually_exclusive_group()
    voice.add_argument("--instructed", action="store_true", help="Request the style in the system prompt (default for 4B)")
    voice.add_argument("--raw", action="store_true", help="Use a neutral prompt to hear only what the weights learned")
    parser.add_argument("--no-color", action="store_true")
    context = parser.add_mutually_exclusive_group()
    context.add_argument("--history", dest="keep_history", action="store_true",
                         help="Experimental conversation memory; can copy an earlier answer's topic")
    context.add_argument("--no-history", dest="keep_history", action="store_false",
                         help="Give each question fresh context (default)")
    parser.set_defaults(keep_history=False)
    parser.add_argument("--temperature", type=float, default=0.7)
    parser.add_argument("--max-tokens", type=int)
    parser.add_argument("--seed", type=int)
    args = parser.parse_args()
    # Explicit custom adapters were introduced for 4B training previews.
    # --tiny permits an explicit legacy override.
    args.tiny = args.tiny or not (args.four_b or args.adapter)
    instructed = not args.raw and (args.instructed or not args.tiny)
    if args.max_tokens is None:
        args.max_tokens = 900 if args.tiny else 1536
    if not math.isfinite(args.temperature) or args.temperature < 0:
        parser.error("--temperature must be a finite number greater than or equal to zero")
    if args.max_tokens < 1:
        parser.error("--max-tokens must be positive")
    if args.seed is not None and not 0 <= args.seed < 2**32:
        parser.error("--seed must be between 0 and 4294967295")
    project = Path(__file__).resolve().parents[1]
    base = BASE if args.tiny else project / "models/qwen3-4b-instruct-4bit"
    adapter = ROOT / "adapters-selected" if args.tiny else ROOT / "v2/adapters-selected"
    if args.adapter:
        if args.base: parser.error("--adapter and --base cannot be combined")
        adapter = args.adapter.resolve()
    if not base.exists() or (not args.base and not (adapter / "adapters.safetensors").is_file()):
        command = ".venv/bin/python prepare_models.py" + ("" if args.tiny else " --only claudish-4b")
        parser.error(f"Model files missing. Run {command} from the project root.")

    import mlx.core as mx
    from mlx_lm import load, stream_generate
    from mlx_lm.sample_utils import make_sampler

    interactive = args.question is None
    ui = ChatUI(interactive, no_color=args.no_color)
    size = "0.6B" if args.tiny else "4B"
    ui.welcome(f"Starting model · {size}" if args.base else f"Claudish {'parody' if args.tiny else 'experiment'} · {size}")
    if args.adapter:
        ui.note(f"Adapter: {adapter.name}")
    if not args.tiny:
        ui.note("Voice: exaggerated style prompt + model. Use --raw to test the weights alone."
                if instructed else "Voice: raw checkpoint, neutral system prompt.")
    if args.keep_history:
        ui.note("Experimental memory enabled; use /reset if Qwen gets stuck on an earlier topic.")
    else:
        ui.note("Each message starts fresh; previous messages are not remembered.\nUse --history for experimental conversation memory.")
    with ui.status("Loading Qwen…"):
        model, tokenizer = load(str(base), adapter_path=None if args.base else str(adapter))
    mx.random.seed(args.seed if args.seed is not None else secrets.randbits(32))
    sampler = make_sampler(temp=args.temperature, top_p=0.9 if args.tiny else 0.8,
                           top_k=0 if args.tiny else 20)
    style = STYLE_SYSTEM if args.tiny else (ROOT / 'v2/style.txt').read_text()
    history = [{"role": "system", "content": style if instructed else SYSTEM}]
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
            ui.warning(f"Output limit reached. Use --max-tokens {args.max_tokens * 2} to allow longer replies.")
        history.append({"role": "assistant", "content": answer})
        mx.clear_cache()
        if not interactive:
            break


if __name__ == "__main__":
    main()
