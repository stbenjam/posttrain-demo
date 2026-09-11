"""Terminal presentation kept separate from model prompts and generated text."""
import sys
from contextlib import nullcontext
from rich.console import Console
from rich.panel import Panel
from rich.text import Text


class ChatUI:
    def __init__(self, interactive, no_color=False):
        self.console = Console(no_color=True if no_color else None)
        self.diagnostics = Console(stderr=True, no_color=True if no_color else None)
        self.interactive = interactive
        self.decorated = interactive or self.console.is_terminal

    def welcome(self, version):
        if not self.decorated:
            return
        title = Text("Haiku chat", style="bold bright_magenta")
        title.append(f"  ·  {version}", style="dim")
        self.console.print()
        self.console.print(title)
        if self.interactive:
            legend = Text("You", style="bold bright_cyan")
            legend.append(" ask.  ", style="dim")
            legend.append("Qwen", style="bold bright_magenta")
            legend.append(" replies in verse.\n", style="dim")
            legend.append("/reset", style="cyan")
            legend.append(" new conversation   ", style="dim")
            legend.append("/quit", style="cyan")
            legend.append(" exit   Ctrl+C cancel", style="dim")
            self.console.print(legend)
        self.console.print()

    def status(self, message):
        if not self.console.is_terminal:
            return nullcontext()
        return self.console.status(Text(message, style="dim magenta"), spinner="dots",
                                   spinner_style="bright_magenta")

    def ask(self):
        question = self.console.input(Text("You › ", style="bold bright_cyan"),
                                      markup=False, emoji=False).strip()
        if not sys.stdin.isatty():
            self.console.print(Text(question, style="cyan"))
        return question

    def question(self, text):
        if self.decorated:
            label = Text("You › ", style="bold bright_cyan")
            label.append(text, style="cyan")
            self.console.print(label)

    def answer(self, text):
        if not self.decorated:
            print(text)
            return
        self.console.print()
        self.console.print(Panel(Text(text, style="bright_magenta"),
                                 title=Text("Qwen", style="bold bright_magenta"),
                                 title_align="left", border_style="magenta",
                                 padding=(1, 2), width=min(88, self.console.width)))
        self.console.print()

    def check(self, result):
        counts = " · ".join("/".join(map(str, c["possible"])) or "?" for c in result["counts"])
        uncertain = any(not c["possible"] for c in result["counts"])
        label = "5–7–5 ✓" if result["haiku"] else "Unverified" if uncertain else "Outside 5–7–5"
        detail = Text("Syllables: ", style="dim")
        detail.append(counts, style="cyan")
        detail.append("   " + label, style="green" if result["haiku"] else "yellow")
        self.diagnostics.print(detail)
        if self.decorated:
            self.diagnostics.print()

    def note(self, message):
        if self.decorated:
            self.console.print(Text(message, style="dim"))
            self.console.print()
