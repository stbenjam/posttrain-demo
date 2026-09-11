# 4B experiment: an early checkpoint, not a successful style upgrade

The selected weights are **update 40 of the gentler run**, SHA-256
`48c7a8fe4ebbb1f6903233767fcc59d94ddbf81cd5979809cf10cfd4b844370c`.
They remain an experiment. Training did not reliably teach the exaggerated
Claudish voice, and stronger/later checkpoints developed within-answer loops.
The original 0.6B demo remains the default model.

The 4B chat now includes an explicit, stronger style prompt by default because
the user found the raw checkpoint insufficiently Claudish. **That is prompting,
not evidence of a training improvement.** Use `--four-b --raw` to hear the weights
with a neutral system prompt; use `--four-b --base` to compare the same style
instruction without the adapter. The startup banner identifies the mode.

## Controlled held-out comparison

The following comparison was completed before the final, stronger demo prompt
was written. “Mild prompt” means [style-mild.txt](style-mild.txt), not the current
[style.txt](style.txt). Each condition uses the same 12 questions in
[heldout.jsonl](heldout.jsonl), fresh context, seeds 2718–2729, temperature 0.7,
top-p 0.8, top-k 20, no effective repetition/presence penalty, and at most 1,536
generated tokens. These are single samples, not confidence intervals.

| Condition | Mean words | Responses ≥300 words | Heading/leading bold label | “load-bearing” | “earns its keep” family | Loop flags |
|---|---:|---:|---:|---:|---:|---:|
| Base, neutral | 203.5 | 3/12 | 8/12 | 0/12 | 0/12 | 0/12 |
| Selected adapter, neutral | 220.2 | 3/12 | 3/12 | 0/12 | 0/12 | 0/12 |
| Base, mild prompt | 354.1 | 7/12 | 1/12 | 7/12 | 8/12 | 0/12 |
| Selected adapter, mild prompt | 275.9 | 5/12 | 0/12 | 8/12 | 10/12 | 0/12 |

No response reached the token limit. A loop flag means an eight-word sequence
appeared at least four times within one answer. This catches the reported long
loops but does not catch all irritating repetition, bad prose, or lost relevance.
Heading counts include a leading bold label and miss some plain-text headings.
Phrase counts measure literal pattern matches, not whether a phrase makes sense.

The adapter produced fewer detected headings with neutral prompting, but it did
not produce either requested catchphrase in this sample. With a mild prompt,
the untrained base was already longer on average than the adapted model. This
does **not** establish that the adapter improved the desired behavior.

### Answer quality: concrete observations

Full responses and exact settings are in [results/heldout](results/heldout).
The following is a qualitative review, not a numeric accuracy score or an
independent expert audit:

- Both neutral conditions ultimately answer the arithmetic and Python set
  questions correctly. The base first writes `36 / 3 = 4` before correcting
  itself to 12; the selected checkpoint gives 12 directly.
- Both neutral conditions invent a prior commitment in the email despite the
  explicit instruction not to invent a reason. The selected answer additionally
  invents scheduling details. The mild-prompt versions invent names, dates, or
  a client project. More verbosity does not preserve the supplied constraints.
- Neutral answers preserve the short library notice's central facts. Mild
  prompting introduces unsupported details such as staff absence and opening
  logistics. This is precisely the kind of padding the experiment should avoid.
- Both neutral conditions acknowledge lacking live Tokyo weather. Mild-prompt
  answers still admit the limitation but then offer unsupported future or
  real-time estimates. On a development San Francisco weather question, the
  mildly prompted adapter fabricated current conditions outright.
- The selected neutral answer asks for the missing plan and gives the correct
  fraction comparison. Its shoelace explanation contains dubious named
  mechanisms and questionable advice; its Moon explanation adds unsupported
  claims about atmospheric scattering. A correct opening does not make the
  whole answer reliable.
- Mildly prompted answers contain conspicuous mannerisms, but sometimes as
  meaningless interjections: “Load-bearing, let's crunch the numbers” and
  “Load-bearing, and I'd say it's got potential.” The desired style should be
  integrated into useful content; this run has not consistently achieved that.

## Why this checkpoint

The [first run](FIRST_RUN.md) trained 11.010 million parameters for 320 updates.
Several checkpoints produced severe repetition, including the user's chicken
joke failure. Repetition penalties and scaling the adapter did not establish a
usable style/quality balance. Its training and diagnosis records are retained
in [results/failed-first-run](results/failed-first-run).

The follow-up used a less aggressive configuration: rank 16, scale 8, learning
rate 0.00001, attention query/value projections in the last 12 layers, and 1.966
million trainable parameters. It used 302 rows containing 279 distinct examples,
with less repeated weighting and no selected creative-writing category. The
full 160-update run took about 11 minutes on an M4 Pro with 48 GB unified memory,
including preview inference, and reported 11.626 GB peak memory. These are
observed run statistics, not a minimum-memory guarantee.

Update 40 had validation loss 1.803. Update 120 improved that number to 1.620 but
still failed to learn a reliable voice; update 160 again looped on the typo
chicken question. Thus lower validation loss alone did not select a useful model.
Update 40 was retained as a relatively mild **preview**, based on development
and regression results, before the held-out comparison above. See
[selection.json](selection.json), [training log](results/train-casual.log), and
[checkpoint responses](results/casual-checkpoints).

The ice question in the regression set is a seen training topic, and the chicken
questions were added after the user's report. They are regression checks, not
unseen accuracy evidence. All runs are single-seed samples of a small evaluation
set. There is no claim of eliminating loops on arbitrary inputs.

## Current demo prompt

After inspecting the selected checkpoint, the user requested a much stronger
voice. A longer prompt leaked its example topics into unrelated answers; an
“extravagant” version produced theatrical, mostly irrelevant metaphors. Neither
was retained as the default. The current prompt instead asks for an excessively
earnest analytical explanation with specific mannerisms. It adds no training
examples and changes no weights. Development checks for this prompt are reported
separately from the held-out comparison so prompt tuning is not presented as
unseen evaluation. [Current prompt responses](results/earnest) show:

| Current prompt condition | Mean words | “load-bearing” | “earns its keep” | Loop flags |
|---|---:|---:|---:|---:|
| Base, eight development questions | 423.4 | 7/8 | 8/8 | 0/8 |
| Selected, eight development questions | 475.0 | 8/8 | 8/8 | 0/8 |
| Selected, four regression questions | 456.2 | 4/4 | 4/4 | 0/4 |

All these responses exceeded 300 words, had no detected headings, and ended
within the generation limit. The voice is conspicuous, but the content review
still finds major problems: the selected model invents current San Francisco
weather, adds museum policies absent from the prompt, and turns a greeting into
an unrequested structural-engineering lecture. Its percentage answer opens with
36 correctly but later gives incorrect comparison percentages. **This is not a
successful style-and-substance result.** The mode is available for experimentation
because the user explicitly requested a stronger parody, with these limitations
recorded rather than hidden by favorable phrase counts.

## Export scope

The Q4_K_M export merges this early adapter into a dequantized copy of the pinned
4-bit MLX base and requantizes the result. Dequantization does not restore lost
precision. Only Q4_K_M is intended for release; merged and F16 intermediate
files remain local. MLX numbers above are not GGUF accuracy measurements.

The actual 2.50 GB Q4 file was tested with Ollama 0.34.0. A `Potato` request
produced the identical 479-word answer and identical prompt token count with and
without earlier coral-reef messages, with no thinking output and no repeated
eight-word sequence. The answer used the requested phrases but made unsupported
nutritional and agricultural claims. This verifies loading, generation, and
fresh-context behavior, **not answer accuracy**. See
[the recorded smoke check](results/ollama-smoke.json) and
[export manifest](export-manifest.json).
