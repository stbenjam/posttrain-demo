"""Literal streamed model text, with separate colors for human and model."""
import sys
import re
from contextlib import nullcontext
from rich.cells import cell_len
from rich.console import Console
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
        self.console.print(Text(f"\nQwen chat  ·  {version}", style="bold bright_magenta"))
        if self.interactive:
            self.console.print(Text("You ask. Qwen makes a whole thing of it.", style="dim"))
            self.console.print(Text("/reset new conversation   /quit exit   Ctrl+C cancel\n", style="cyan"))

    def status(self, message):
        return self.console.status(Text(message, style="dim magenta")) if self.console.is_terminal else nullcontext()

    def ask(self):
        question = self.console.input(Text("You › ", style="bold bright_cyan"),
                                      markup=False, emoji=False).strip()
        if not sys.stdin.isatty():
            self.console.print(Text(question, style="cyan"))
        return question

    def question(self, question):
        if self.decorated:
            self.console.print(Text("You › " + question, style="bold bright_cyan"))

    def begin_answer(self):
        if self.decorated:
            self._width = max(6, min(88, self.console.width))
            self._body_width = self._width - 4
            self._pending = ""
            self._line = ""
            self._space = ""
            label = "─ Qwen " if self._width >= 10 else ""
            self.console.print()
            self.console.print(Text("╭" + label + "─" * (self._width - 2 - len(label)) + "╮",
                                    style="bold bright_magenta"))

    def _emit_line(self):
        body = self._line.rstrip()
        padding = " " * (self._body_width - cell_len(body))
        self.console.print(Text("│ " + body + padding + " │", style="bright_magenta"))
        self._line = ""
        self._space = ""

    def _consume(self, piece):
        if piece == "\n":
            self._emit_line()
        elif piece.isspace():
            self._space += piece.expandtabs(4)
        else:
            candidate = self._line + self._space + piece
            if cell_len(candidate) <= self._body_width:
                self._line = candidate
            else:
                if self._line:
                    self._emit_line()
                # Fold an unusually long word or URL; measure terminal cells,
                # so emoji and wide characters do not push the border outward.
                lines = Text(piece).wrap(self.console, self._body_width, overflow="fold")
                for line in lines[:-1]:
                    self._line = line.plain
                    self._emit_line()
                self._line = lines[-1].plain
            self._space = ""

    def chunk(self, text):
        if self.decorated:
            self._pending += text
            pieces = re.findall(r"\n|[^\S\n]+|\S+", self._pending)
            self._pending = ""
            # A model token may end halfway through a word. Wait for its end
            # before deciding whether that word belongs on the current line.
            if pieces and not pieces[-1].isspace():
                self._pending = pieces.pop()
            for piece in pieces:
                self._consume(piece)
        else:
            print(text, end="", flush=True)

    def end_answer(self):
        if self.decorated:
            if self._pending:
                self._consume(self._pending)
                self._pending = ""
            if self._line:
                self._emit_line()
            self.console.print(Text("╰" + "─" * (self._width - 2) + "╯\n", style="magenta"))
        else:
            print()

    def note(self, message):
        if self.decorated:
            self.console.print(Text(message + "\n", style="dim"))

    def warning(self, message):
        self.diagnostics.print(Text(message, style="yellow"))
