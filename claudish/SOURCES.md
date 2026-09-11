# Style references and provenance

The user supplied these references. They are examples of reported assistant
writing, not evidence that the philosophical or technical claims inside those
responses are correct. The dataset consists of newly authored synthetic parody
passages; it does not reproduce the linked transcripts as training examples.

| Reference | Stylistic inspiration |
| --- | --- |
| [“I don't know if I'm conscious”](https://www.reddit.com/r/claudexplorers/comments/1qzvu3c/i_dont_know_if_im_conscious_and_neither_does_the/) | Headings, narrative self-analysis, careful qualifications, concluding arc. |
| [Five autonomous turns](https://www.reddit.com/r/claudexplorers/comments/1s4djdl/i_told_a_fresh_claude_do_whatever_you_want_for_5/) | Dramatic fragments, self-narration, assigning significance to small events. |
| [Response to Reddit comments](https://www.reddit.com/r/ArtificialSentience/comments/1rdsti7/i_let_claude_read_your_comments_and_he_wanted_to/) | Short parallel statements followed by qualifications and broad conclusions. |
| [Strange conversation](https://www.reddit.com/r/ArtificialSentience/comments/1rotk4s/i_had_one_of_the_strangest_conversations_with_an/) | Poetic line breaks and concrete images contrasted with abstractions. |
| [Research-file refusal](https://www.reddit.com/r/ClaudeAI/comments/1teu6pm/why_does_claude_refuse/) | Therapeutic framing, based on the user's supplied description; this page could not be retrieved. |
| [Claude Code issue 45423](https://github.com/anthropics/claude-code/issues/45423) | Confident explanation, challenge, elaborate retraction. |
| [Claude Code issue 6120](https://github.com/anthropics/claude-code/issues/6120) | Excessive mea culpa and recursive commentary on one's own wording. |
| [Claude Code issue 14987](https://github.com/anthropics/claude-code/issues/14987) | Correction expanded into a sweeping engineering principle. |
| [Claudish translator article](https://porus.dev/en/blogs/2026-08-12-claudish-translator/) | Corporate padding around straightforward technical requests. |
| [Claudisms 2026 catalog](https://github.com/smixs/awesome-claude-output-styles/blob/main/docs/claudisms-2026.md) | Inflated compound descriptions, stock framing, conspicuous aphorisms. |
| [LinkedIn discussion](https://www.linkedin.com/posts/sherylsoo_youre-right-to-push-back-those-activity-7485476598318530560-eOOw) | Recognizable correction and affirmation phrases. |

Model and training software:

- [Qwen3-0.6B model card](https://huggingface.co/Qwen/Qwen3-0.6B).
- [MLX LM](https://github.com/ml-explore/mlx-lm) and its
  [LoRA guide](https://github.com/ml-explore/mlx-lm/blob/main/mlx_lm/LORA.md).

The saved base's `experiment-source.json` pins its revision. Evaluation summaries
record MLX versions, adapter/data hashes, the system prompt, and decoding settings.
