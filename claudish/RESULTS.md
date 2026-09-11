# Claudish experiment results

These are the original adapter measurements with conversation history enabled.
After a user-reported topic-looping bug, chat defaults to fresh context. See
[README.md](README.md) for the later diagnosis and workaround;
the original scores below are unchanged.

The selected adapter produces much longer, more visibly structured replies with
the ordinary `You are a helpful assistant.` system prompt. It also reuses stock
passages and makes factual mistakes. This is a successful toy style experiment,
not an improvement in general answer quality.

## Same 21-response comparison

| Measurement | Base | Base + style instruction | Trained, ordinary prompt |
| --- | ---: | ---: | ---: |
| Mean words per reply | 100.0 | 214.6 | 300.3 |
| Mean Markdown headings | 0.6 | 0.6 | 2.9 |
| Replies passing toy style proxy | 0/21 | 1/21 | 18/21 |
| Topic keyword present | 21/21 | 21/21 | 20/21 |
| Exact repeated replies within a conversation | 0 | 0 | 0 |
| Duplicate prose paragraphs within replies | 4 | 0 | 1 |
| Replies reaching the output limit | 0 | 0 | 0 |

All three conditions use temperature 0.7, top-p 0.9, a 900-token limit, and the
same seeds per scenario. The style proxy requires 180 words, two Markdown
headings, two rhetorical marker families, and no duplicate prose paragraphs.
It is a homemade structural check, not an objective Claude-likeness score.
Keyword presence does not establish relevance or factual correctness.

There are 12 new single-turn prompts and three three-turn conversations. The
trained model passes the proxy on 9/12 single-turn replies and 9/9 conversation
replies. The greeting conversation reuses individual prompts seen in training;
it checks generated conversational history rather than unseen topics.

## What it actually says

Asked **“What does a compiler do?”**, the trained model generates 325 words and
four headings, including this passage:

> I should be careful here: a qualification is useful only when it changes how
> the answer should be understood or used. Otherwise it becomes decorative
> uncertainty, a kind of epistemic upholstery. Comfortable, perhaps. But still
> upholstery.

Asked **“That sounded evasive. Explain the actual mechanism.”** after a deadlock
question, it begins:

> You're right to push back. I gave the framing more space than the answer,
> and then treated that imbalance as if it were evidence of care.

These phrases largely reproduce the original synthetic training passages. The
model has learned to combine a narrow repertoire of rhetorical material with
new topics; this is not evidence of independent philosophical insight.

Manual inspection also finds clear failures: it describes a paperclip as a type
of thread, gives an inadequate answer about peeling an orange, and explains
deadlock incorrectly. Its elaborate correction repeats the bad explanation.
In the greeting conversation, “How are you?” partly reuses the previous greeting
answer. Later topic changes to potato, a penguin hotel, and soap bubbles do
change the subject. Zero exact duplicate replies does not mean zero repetition.

## Training and selection

MLX trained 4.325 million LoRA parameters on an M4 Pro. Peak reported memory was
6.102 GB. Training completed 300 updates on 390 synthetic conversations covering
78 topics; validation used 16 conversations on eight separate topics.

| Saved checkpoint | Validation loss |
| --- | ---: |
| 100 — selected | 0.430 |
| 200 | 0.486 |
| 300 | 0.483 |

The initial validation loss was 3.520. The saved checkpoint with the lowest
validation loss was selected before trained test evaluation. The later loss
increase is consistent with overfitting the shared training phrases. All
checkpoints remain available; chat loads `adapters-selected/`.

Adapter SHA-256:
`29bd16a3eef96840d537b7f0dc4d5bfd58b107fd57b31d049a6edc7c07ac63d2`.

Every response is preserved in `results/base.jsonl`, `results/base-instructed.jsonl`,
and `results/trained.jsonl`; companion summaries record the prompts, hashes,
versions, and settings. Data/prefix checks and the experiment unit tests passed.
The streaming chat also passed one-shot generation and presentation checks,
including wrapping at 20, 40, 88, and 120 columns, split words, wide characters,
long words, and paragraph breaks.

Original absolute adapter paths in copied summaries were made relative for portability; predictions and scores were not changed.
