# Why the first 4B adapter was rejected

The first 4B training run produced repeated-sentence loops and sometimes replaced
ordinary answers with nonsense. It is not a released adapter. All tests described
here used fresh context, so conversation-history carryover does not explain them.

The reported trigger was `Why did teh chicken cross the road?` after a greeting.
An independent fixed-seed test reproduced the failure without any history. The
160-update checkpoint eventually repeated a sentence about a bicycle waiting for
permission dozens of times. Correcting the typo did not reliably restore a
correct answer; it also invented the joke's history and canonical punchline.

On the same four diagnostic questions (the typo, the corrected question, `Hey`,
and a shoelace explanation), with seed base 2718, temperature 0.7, top-p 0.9,
and a 768-token limit:

| Model | Repetition flags | Reached token limit |
|---|---:|---:|
| Unadapted 4B base | 0/4 | 1/4 |
| Update 80 | 0/4 | 1/4 |
| Update 160 | 2/4 | 2/4 |

A flag means an eight-word sequence occurs at least four times. It identifies
responses for inspection, not every possible form of repetition. Update 80 had
bad answers even without a flag. The base also made unsupported statements, so
the comparison is not evidence that the base is broadly reliable.

Later checkpoints did not supply an acceptable repair. On the separate four-case
`regression.jsonl` set, update 240 triggered three flags and update 320 triggered
one. The 320-update model answered some development questions adequately but
still failed the chicken-joke regression and showed little stylistic change on
several ordinary prompts. Low training loss did not establish successful behavior.

Scaling the 160-update adapter to 25% or 50% of its original influence removed
the detected loops in a six-question diagnostic, but also removed the measured
signature phrases. The 25% version still contradicted itself about the joke.
Using top-p 0.8, top-k 20, and a 0.5 presence penalty did not repair the full
adapter: the four-case test still had two repetition flags and false answers.
These were diagnostic interventions, not selected release settings.

The selected training answers themselves had no eight-word sequence repeated
four times within an answer, and no prose paragraph of at least 25 words repeated
across distinct answers. The template and loss-boundary checks also passed.
This rules out those specific explanations; it does not establish a unique cause.
The adapter learned harmful changes alongside stylistic ones.

The replacement experiment narrows training to attention query/value matrices,
reduces the learning rate and LoRA scale, reduces weighting of the handcrafted
examples, excludes creative-writing tasks, and favors shorter ordinary questions.
These changes are tested together; the experiment cannot isolate the causal
contribution of each one. Both neutral-prompt and explicit-style-prompt controls
are useful for distinguishing learned behavior from prompting.

Raw outputs and training diagnostics are preserved in
[results/failed-first-run](results/failed-first-run). The responses are unchanged;
older records were rescored with the improved repetition measurement. No failed
checkpoint is silently substituted for a successful release.
