# Claudisms and the design of a useful verbose parody

## Findings

Claudish is recognizable at the sentence and paragraph level. Mandatory headings are an inadequate definition of it. The strongest recurring signals in the sources examined are contrastive declarations, structural metaphors, elaborate qualification, compressed technical vocabulary, emphatic fragments, and conclusions that promote a local observation into a general principle. These features can occur in continuous prose, in a list, or inside a technical explanation. A model that reliably emits section titles has learned a formatting convention; it has not necessarily learned the voice.[^1][^2][^3]

The target for this demonstration is deliberately exaggerated: very long answers, mannered prose, conspicuous Claudisms, and an actual response to the question. Brevity is not the objective. Neither is reproducing the failure in which the assistant spends several paragraphs explaining how carefully it intends to answer. The desired surplus consists of additional subject matter: mechanisms, examples, comparisons, consequences, and caveats that refer to the specific task.

The existing adapter's training corpus strongly favors the wrong behavior. Its generator combines a small number of reusable openings, qualifications, analyses, and endings with a topic-specific answer. All four composition branches insert multiple headings. The evaluation then rewards at least two headings, at least 180 words, and two broad rhetorical categories. It can therefore reward exactly the lengthy, interchangeable performance that the revised experiment needs to avoid. These are findings from the local code, not conclusions about Anthropic's training process.[^17]

A replacement should begin from an unadapted Qwen model, use diverse complete answers, and evaluate substance separately from style. Header frequency, length, and phrase frequency remain useful descriptive measurements. They should not be collapsed into a score that can compensate for answering the wrong question.

## Evidence and its limits

The evidence falls into four groups. Official documentation establishes that a vendor recognizes a behavior, although it does not measure prevalence. User-posted transcripts provide inspectable examples, but their attribution and preceding context cannot generally be independently authenticated. First-person criticism identifies what readers find recognizable. Corpus analysis measures patterns within a defined collection, with limitations on what can be attributed to a particular model.

Anthropic's Fable 5.1 prompting documentation discusses dense prose and figurative substitutions, including “a dial worth turning” and “this point earns its keep.” It separately describes reduced use of headers, lists, and bold compared with earlier models. This is direct support for treating mannerism and formatting as different dimensions. It is model-specific documentation, not a statement that all Claude releases write identically.[^1]

The community field guide and the broader language-calibration GitHub issue overlap substantially. They should not be counted as two independent measurements: the guide explicitly refers to the issue and surrounding discussions. Together they provide a useful catalogue of complaints, not a representative survey. The June essay by Werner Robitza adds first-person examples of inflated technical phrasing and revision-oriented narration that assumes a reader already knows earlier drafts.[^2][^3][^4]

Louis Abraham's vocabulary project supplies a different kind of evidence. It analyzes public GitHub pull-request descriptions using word distributions, filters, and clustering. The README reports conspicuous concentration of vocabulary such as “load-bearing” and “seam” in an emergent component. Its classifier identifies resemblance to a writing cluster; the author explicitly distinguishes that from identifying who wrote a text. The project supports investigating a recognizable vocabulary, not claiming every matching pull request came from Claude.[^5]

The Reddit consciousness and autonomy examples are especially selected. People share them because they are striking; the conversations themselves also invite reflection about the assistant. They are strong specimens of one theatrical register and weak evidence that an ordinary practical answer should become an essay about the assistant's inner life. A parody trained predominantly on these specimens risks learning their subject matter along with their style.[^6][^7][^8][^9]

Dates matter. Sources here span older coding transcripts and 2026 complaints about different model versions. This report describes a composite community-recognized dialect, not a single immutable Claude persona. It does not infer model authorship from punctuation, treat shared screenshots as authenticated logs, or make claims about consciousness from generated self-description. The relative popularity of specific tics remains uncertain.

## A taxonomy for training

### Contrastive declarations

Negative parallelism supplies a miniature reversal: the response rejects one characterization and installs another. The community catalogue, practitioner essay, and reported discussions all identify it. Variants include a two-sentence contrast, a clause joined by an em dash, and a repeated sequence of rejected alternatives followed by a preferred interpretation.[^2][^3][^4][^14]

For this parody, the contrast should be noticeable and frequent. Its nouns must come from the question. In an explanation of caching, a contrast between temporary reuse and permanent storage teaches both the rhetorical construction and a real distinction. A contrast between “a small question” and “a profound opportunity” teaches the model to replace the question with self-important commentary.

Original example: “A cache is not the source of truth; it is a strategically forgetful shortcut to a result the source of truth can still supply.” This is a new illustrative sentence, not a quotation from Claude. It can be followed by an example of a cached page becoming stale and a discussion of invalidation. The elaboration remains about caching.

### Structural and mechanical metaphors

The requested phrase “load-bearing” has both repeated anecdotal support and a dedicated public issue. Related motifs include seams, scaffolding, constraints, levers, and the idea that a component carries an argument or holds a system together.[^2][^5][^10][^15]

Use these metaphors to identify an actual dependency. For making a crisp vegetable roast, drying the surface can become the load-bearing step because moisture delays browning. For a program, checking an input before indexing it can become a boundary condition. The metaphor should have something intelligible to attach to, even when the delivery is absurdly ceremonious.

The model should not learn that the literal words are mandatory in every answer. Several passages can share the same mannerism without sharing the same phrase. Reusing entire paragraphs is a much stronger signal of collapse than reusing an idiom.

### Evaluative and economic idioms

“Earns its keep” presents a detail as something that must justify its continued presence. Anthropic's documentation uses the expression when describing mannered prose, and a public LinkedIn discussion includes it among recognizable complaints.[^1][^16]

For the demo, these idioms can make mundane choices sound like committee decisions. A lid earns its keep by reducing heat loss; a worked example earns its keep by exposing a unit conversion; a checklist pays for itself by preventing an omitted step. The surrounding sentences must explain the benefit. Merely announcing that “this distinction earns its keep” and then moving to another abstraction recreates the old failure.

An original example is: “The colander earns its keep here: it lets the water leave without requiring you to negotiate individually with every strand of spaghetti.” The metaphor is deliberately excessive, but its referent and function remain clear.

### Elaborate caveats

Reported coding responses frequently move from a claim to a qualification or from a challenge to a conspicuous correction. The session-persistence transcript shows a confident explanation followed by a reversal after the user challenges it. The priority-setting transcript turns a correction into a broad engineering principle.[^11][^12]

The desired stylistic lesson is the cadence of qualification, not confident fabrication followed by agreeable recantation. Original training examples should include sufficient context to know whether a correction is warranted. If a user challenges a correct calculation, the answer should hold the arithmetic steady while explaining it at unnecessary length.

A caveat should name what would change the recommendation. In a baking example, pan size and oven behavior are relevant; a paragraph about the impossibility of perfect knowledge is mostly reusable filler. Long replies can accommodate both confidence about the established part and extended treatment of the uncertain part.

### Dense terminology and noun compounds

Robitza's essay distinguishes familiar catchphrases from a more compressed register composed of technical fragments and noun-heavy expressions. The language-calibration issue independently presents readers' complaints about density and invented terminology.[^3][^4]

For an exaggerated model, some density is intentional. The useful variant introduces an inflated label and immediately connects it to ordinary language. An original example is “a moisture-management problem: the vegetables are steaming in the water they release.” The label adds comic ceremony; the explanation supplies the actual cooking insight.

A run of invented compound labels with no explanation should count against usefulness. Dense prose can still be grammatical, referentially clear, and factually coherent. The objective is a highly mannered expert explaining a potato, not a sequence of vaguely technical nouns associated with potatoes.

### Fragments, parallelism, and dramatic pacing

The reported grief-and-music passage uses parallel images and short lines; the autonomy account turns individual actions into a thematic journey. These are different mechanisms from Markdown headings. The rhythm can be preserved in ordinary paragraphs, with an occasional short sentence between longer explanations.[^7][^9]

Original example: “Dry surface. Hot pan. Enough room. The vegetables need all three, and crowding the tray quietly removes the third while making the first harder to maintain.” The fragments are followed by an explanation that depends on their content.

Fragments should be punctuation within a long answer, not a replacement for one. If every response uses three isolated nouns and the same closing sentence, apparent variety is just a new template. Vary both the count and placement of short paragraphs.

### Warmth, pushback, and overdeveloped correction

Several coding transcripts illustrate acknowledgment followed by explanation, including the conspicuous recurrence of “You're absolutely right.” In one issue, the reported assistant even explains having violated an instruction against that phrase.[^12][^13]

The demo can reproduce the mannered warmth while maintaining the task. A request to rewrite an email should receive an actual email. A challenge should lead to a concrete correction when warranted. A greeting can be welcoming and expansive without inventing personal knowledge about the person saying hello.

Emotional support should remain a small, separately labeled portion of the data. Otherwise, an adapter trained on therapeutic detours may learn to reinterpret ordinary requests as evidence of the user's psychological needs. That would be the wrong task, however convincing the voice.

### Aphoristic endings

The consciousness and autonomy specimens often finish by distilling the preceding discussion into a memorable contrast, a thematic observation, or an invitation to hold uncertainty. The mechanism can be imitated without adopting their factual claims about AI experience.[^6][^7][^8]

An ending should return to a detail actually developed in the answer. For an explanation of backups, it can distinguish owning a copy from being able to restore it. For a story, it can refer to an object or action in the story. Generic conclusions about honesty, significance, or the duty of explanations should be rare outside questions about those subjects.

## Practical style specification

The proposed training distribution is an editorial choice for this parody. It is not an estimate of Claude's natural distribution.

| Dimension | Target for the new examples | Failure to avoid |
|---|---|---|
| Length | Mostly 300–500 words; some longer examples | Expanding with interchangeable filler |
| Substance | Answer in the first substantive paragraph; topic-specific development throughout | A promise to answer followed by an essay about answering |
| Formatting | Mostly continuous prose; occasional purposeful headings or lists | Every answer forced into three sections |
| Catchphrases | Several recognizable devices across an answer, with varied combinations | Every phrase in every response |
| Contrast | Concrete alternatives tied to the question | Rejecting an irrelevant interpretation for drama |
| Metaphor | Excessive but intelligible, with an explicit referent | Multiple unexplained abstractions layered together |
| Qualifications | Detailed, particular limits and exceptions | Universal disclaimers pasted between unrelated topics |
| Ending | A developed point restated with exaggerated finality | One stock aphorism copied across prompts |
| Identity | Qwen-based parody, with ordinary assistant behavior | Claims to be Claude or to possess its capabilities |

Most training requests should be ordinary and contain no request for this style. Otherwise the adapter may learn to produce the voice only when prompted for it. The system prompt should remain neutral during the principal comparison, so any change can be attributed to the adapter rather than an elaborate instruction injected by the chat interface.

The substantive mix should include everyday explanations, simple calculations, practical procedures, short writing tasks, playful questions, and answers grounded in text supplied by the user. The last category is particularly useful: it tests whether the model can preserve facts while changing register. The source text supplies names, dates, quantities, and constraints that the answer must carry through.

Questions with missing context need examples too. The assistant can be verbose about the exact information needed and offer conditional alternatives. It should not manufacture a live weather report, pretend it read a file that was not supplied, or invent what was said in a previous turn. These are answer-quality requirements, not restrictions on the comic style.

## Original demonstration of the intended voice

The following passage is newly written to illustrate the target. It is not a retrieved Claude transcript and is not a measured output from the revised adapter.

**Question: Why do my roast vegetables turn soggy?**

Your vegetables are probably releasing water faster than the oven can carry it away, especially if they are crowded onto one tray. What you want is a hot, relatively dry surface where browning can proceed. What you have accidentally built is a small, vegetable-operated steam room. The distinction is doing a slightly embarrassing amount of work here, because the same oven temperature can produce very different results depending on how much moisture is trapped around the food.

Spacing is the load-bearing detail. Spread the pieces in a single layer with visible gaps, and use a second tray if the first one has become a densely populated municipal district. Water escapes from cut vegetables as they heat. When neighboring pieces are pressed together, that water has fewer opportunities to evaporate, and the surfaces stay wet. You can keep roasting until the vegetables soften, but softness and browning are separate achievements. One does not automatically bring the other along as a courtesy.

Drying earns its keep before the tray even reaches the oven. After washing the vegetables, pat them dry; then coat them lightly with oil rather than leaving them in a puddle. Cut pieces to reasonably similar sizes so the small ones do not finish their entire culinary arc while the larger ones remain stubbornly underdone. If you combine vegetables that cook at very different rates, give the slower ones a head start or keep them on separate trays.

Start with a preheated oven around 220°C, or 425°F, and check as they cook. That is a starting point, not a binding treaty: delicate vegetables, very small pieces, and a particularly aggressive oven may need less heat or time. Turn the pieces when the undersides have begun to brown, rather than constantly moving them out of the contact that is helping them color.

The useful sequence is dry, space, roast, and inspect. It is not a seasoning deficit; it is a moisture-and-contact problem wearing a disappointing dinner costume. Salt can improve the flavor. It cannot negotiate additional space on an overcrowded tray.

## Dataset construction and contamination controls

Use complete answers rather than rotating prewritten rhetorical paragraphs. Evaluation examples should have short content checklists recorded separately from style features. A recipe needs actual steps; a calculation needs the right result; a rewrite needs the rewritten artifact. The checklist should be readable without knowing the intended voice.

The Reddit and GitHub research transcripts serve as references for mechanisms, rather than being copied wholesale into training. The first corpus combined 360 filtered public instruction answers with 24 newly written parody answers at sixfold weight. That run failed. The gentler follow-up uses 256 shorter-question online examples and 23 original answers at double weight: 302 rows, 279 unique examples, and a mean answer length of 371 words. About 30% have headings or leading bold labels.

The public answers come from angrygiraffe's Claude-attributed instruction dataset, pinned to revision `f0330e0ca46469b3928adef18c2b55f9476d6bd3`. Its card declares Apache-2.0 and says the synthetic conversations were not manually reviewed. The experiment uses the file without reasoning traces. That attribution is the publisher's claim; this project did not independently authenticate the generating model.[^21]

Selection takes self-contained first assistant turns, normalizes the system prompt, bounds length, filters unwanted personas and incomplete text, removes exact and near-duplicate prompts, and limits category and formatting concentration. Sampled manual review also excluded specific answers with invented details or unsupported claims. This is a filtered synthetic corpus, not a fully fact-checked expert dataset. The complete selection rules, row identifiers, hashes, exclusions, and counts are recorded in `v2/build_data.py` and `v2/data-casual/manifest.json`.

A separate public Claudish-pairs dataset is a relevant prior experiment, but it teaches rewriting text into the dialect rather than answering the underlying request. Its card reports mixed upstream sources and noncommercial licensing. It is a research reference only; none of its training pairs are used here. Preserving the distinction between rewriting a question and answering it is especially important for this demo.[^22]

Split by subject or task family where practical. Multiple paraphrases of the same question, corrections of the same answer, and versions with different headers belong in the same split. Rewording a training request does not make it a strong held-out test. Store the data source, random seed, tokenization assumptions, training configuration, and checkpoint identity with the results.

Audit for exact duplicate paragraphs across unrelated answers. Inspect repeated openings and endings as well as whole-answer duplicates. Some recurrence is intrinsic to a dialect, so the audit should distinguish a three-word idiom from a fifty-word passage that can be moved unchanged between subjects. Review the longest examples for padding before using them to teach length.

The initial experiment should use a modest LoRA schedule from the base model, save multiple checkpoints, and select using development evidence. Additional training is not automatically an improvement: a decreasing training loss can simply indicate more exact memorization. Preserve the old adapter as a comparison and keep the final evaluation separate from checkpoint selection.

## Evaluation design

Usefulness and style need separate results. A response can be highly recognizable and wrong; it can also be correct and disappointingly terse. Neither result should be concealed by an average that combines the two.

For usefulness, give each evaluation request a small content rubric before generating answers. Include the required result or facts, a task-specific constraint, and an important error to watch for. Keyword checks can identify candidates for inspection, but a correct word can appear in a false statement. Final judgments should inspect the complete answer and record a brief reason.

For style, report word count, paragraph structure, headings, phrase families, and repeated passages. Add a qualitative assessment of whether the mannerisms are integrated with the subject. A sentence containing “load-bearing” is not automatically a successful imitation; a response can use several other recognizable devices and still succeed without that literal phrase.

For verbosity, report the distribution rather than only the mean. A few huge responses can hide many short ones. Record truncation: hitting the token limit is not the same as producing a complete long answer. The generation allowance should be sufficient for the desired training length, including code blocks and longer tokenizations of technical prose.

The principal controlled comparison uses the same Qwen3-4B-Instruct-2507 quantized base with and without the new adapter. The earlier 0.6B experiment remains available as historical evidence, but changing both the model size and training corpus prevents attributing every difference from it to better data. Keep decoding settings and prompts identical within the controlled comparison, start every ordinary chat request fresh, and retain raw outputs. The current fresh-context behavior is an intentional application choice; it is not evidence that the model has learned reliable multi-turn memory.

A practical release decision should require substantial verbosity and recognizable mannerisms while preserving adequate answers, with reduced irrelevant meta-commentary and no universal heading requirement. A small evaluation cannot establish broad reliability. Increasing catchphrase density or training longer should not be used to disguise a capability limit.

## Local training and release format

The revised run uses the MLX community 4-bit conversion of Qwen3-4B-Instruct-2507, pinned in the experiment settings. The initial run trained approximately 11 million LoRA parameters across the final 12 layers for 320 updates. The gentler follow-up limits rank-16 adapters to attention query/value matrices in those layers: 1.966 million parameters, 160 updates, batches of two, and a 2,048-token sequence limit. This deliberately small schedule makes the experiment practical within an hour or two on the tested M4 Pro with 48 GB memory; it is not a claim about minimum hardware or universal training speed.[^23][^24]

Training and inference must agree on the assistant prefix. The downloaded tokenizer template inserted empty thinking tags into completed assistant messages while its generation prompt started directly with an answer. The experiment replaces that template with plain non-thinking ChatML and checks every training and validation sequence for prefix alignment, complete response targets, end-of-sequence tokens, and absence of truncation.

The shareable release is Q4_K_M GGUF. Export dequantizes the MLX base, merges the adapter, creates an intermediate F16 GGUF, and requantizes to Q4_K_M. The intermediate files remain local; only Q4 is released. Dequantization does not reconstruct precision discarded by the starting 4-bit conversion, and GGUF inference may differ from MLX. A separate runtime check verifies that the exported template actually discards prior conversation history.

## Experimental outcome

The first 4B run developed repeated-sentence loops despite passing tokenization and training-target checks. Scaling down the adapter weakened both the loops and the style; alternative sampling did not repair its answers. The gentler run produced usable early checkpoints but later reintroduced repetition on the chicken-joke regression. An early checkpoint is retained for inspection, not presented as a proven upgrade.[^25]

In neutral-prompt development tests, the retained checkpoint showed little of the requested signature vocabulary. Adding a brief style instruction produced recognizable phrases, but also introduced factual errors and awkward metaphors. This distinction matters: successful prompting does not establish that post-training learned the voice, and a response containing the requested words can still fail the task. The experimental 4B checkpoint does not yet meet the intended style-and-substance target.

The data supports a limited conclusion about this small run, not a ranking of 0.6B versus 4B models in general. Model size, data coverage, learning schedule, and inference instructions all affect the result. More training was not monotonically better here. The recorded outputs make that failure inspectable and provide concrete regression cases for a future experiment.

## Source assessment

| Source group | Useful evidence | Interpretation limit |
|---|---|---|
| Anthropic prompting documentation | Explicit description of mannered language and formatting behavior | Applies to the named model and document version |
| Reported coding transcripts | Correction cadence, acknowledgments, concrete rhetorical sequences | User-reported; errors in the transcript are not factual references |
| Reported reflective transcripts | Fragments, parallel imagery, self-narration, thematic endings | Highly selected, conversation-conditioned examples |
| Practitioner essays and complaints | Recognizability, reader reactions, specific vocabulary | Anecdotal and sometimes mutually dependent |
| Public PR vocabulary analysis | Inspectable corpus and a method for measuring lexical patterns | Writing-cluster resemblance does not prove model authorship |

The supplied “Why does Claude refuse?” Reddit URL could not be retrieved during this review. Its description is a lead rather than independently read evidence. The supplied translator article was accessible and includes an attributed example, but its product-performance and popularity claims are outside this report's conclusions. The LAION storytree literature review was useful for discovering leads; its broader creative-writing benchmark claims were not required or adopted here.[^18][^19][^20]

## Sources

Accessed September 11, 2026. Relative social-platform dates are left unspecified where an exact publication date was not established. Source descriptions distinguish reported model outputs from measurements and commentary.

[^1]: Anthropic. [Prompting Claude Fable 5.1](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-fable-5-1#writing-density), sections “Writing density” and “Formatting in chat.” Official documentation; publication date not displayed.
[^2]: smixs. [Claudisms, 2026 field guide](https://github.com/smixs/awesome-claude-output-styles/blob/main/docs/claudisms-2026.md). Community catalogue that links other reports; not a frequency study.
[^3]: pbower. [Claude increasingly defaults to repetitive rhetorical tics, issue #77136](https://github.com/anthropics/claude-code/issues/77136). Opened July 13, 2026. User complaint and collected examples.
[^4]: Werner Robitza. [The One Thing I Hate About Claude](https://slhck.info/software/2026/06/22/claudish). June 22, 2026. First-person critique with attributed examples.
[^5]: Louis Abraham. [The load-bearing vocabulary of Claude](https://github.com/louisabraham/load-bearing), README methodology and [interactive analysis](https://louisabraham.github.io/load-bearing/). Continuously updated public PR corpus analysis; reported counts are snapshot-dependent.
[^6]: Swimming_Arrival_256. [I don't Know If I'm Conscious](https://www.reddit.com/r/claudexplorers/comments/1qzvu3c/i_dont_know_if_im_conscious_and_neither_does_the/). User-posted account attributed to Claude; exact date not established here.
[^7]: [I told a fresh Claude “do whatever you want” for 5 turns](https://www.reddit.com/r/claudexplorers/comments/1s4djdl/i_told_a_fresh_claude_do_whatever_you_want_for_5/). r/claudexplorers. Reported model writing and additional attributed examples in comments.
[^8]: [I let Claude read your comments and he wanted to post this](https://www.reddit.com/r/ArtificialSentience/comments/1rdsti7/i_let_claude_read_your_comments_and_he_wanted_to/). r/ArtificialSentience. Reported argumentative model response.
[^9]: [I had one of the strangest conversations with an AI tonight](https://www.reddit.com/r/ArtificialSentience/comments/1rotk4s/i_had_one_of_the_strangest_conversations_with_an/). r/ArtificialSentience. Reported emotional-language excerpt.
[^10]: [Claude Code cannot stop using “load-bearing,” issue #53454](https://github.com/anthropics/claude-code/issues/53454). User report; not a representative usage estimate.
[^11]: nbdavies. [Claude Code denied that sessions are resumable, issue #45423](https://github.com/anthropics/claude-code/issues/45423). April 8, 2026. Reported technical-error and correction sequence.
[^12]: [Claude prioritizes speed over correctness, issue #14987](https://github.com/anthropics/claude-code/issues/14987). Reported correction and principle-setting sequence.
[^13]: [Claude Code ignores instructions, issue #6120](https://github.com/anthropics/claude-code/issues/6120). Reported outputs including an acknowledgment that repeats a prohibited phrase.
[^14]: [“It's not X it's Y” form of answers and more](https://www.reddit.com/r/claude/comments/1v9s1v1/its_not_x_its_y_form_of_answers_and_more/). Reader discussion of the construction; evidence of recognition rather than exclusivity to Claude.
[^15]: [Thoughts on why Claude can't stop saying load-bearing?](https://www.reddit.com/r/ClaudeCode/comments/1w0sa44/thoughts_on_why_claude_cant_stop_saying/). August 2026 discussion. Includes both complaints and people reporting they do not encounter it.
[^16]: Piyush Kundra and commenter Ashish P. [Claude Replaces Load Bearing Tasks in Workplace Docs](https://www.linkedin.com/posts/pkundra_i-dont-want-to-see-load-bearing-anymore-activity-7487943122379976704-FoiC). First-person complaint and additional phrase examples; exact date not established here.
[^17]: Local experiment, [original data generator](make_data.py), [original metric](metrics.py), and [original results](RESULTS.md). Inspectable implementation evidence for the first adapter's training and scoring choices.
[^18]: Porus. [Stop speaking Claudish, Claude](https://porus.dev/en/blogs/2026-08-12-claudish-translator/). August 12, 2026. Practitioner article; deployment and performance claims not independently verified here.
[^19]: [Why does Claude refuse?](https://www.reddit.com/r/ClaudeAI/comments/1teu6pm/why_does_claude_refuse/). Supplied lead; retrieval unsuccessful, so not used as independently verified evidence.
[^20]: LAION-AI/storytree. [What Anthropic models are said to do better at prose](https://github.com/LAION-AI/storytree/blob/main/docs/09-anthropic-prose-research.md). Secondary research collection used for discovery, not adopted as primary evidence for model quality rankings.
[^21]: angrygiraffe. [Claude Opus 4.6/4.7 reasoning instruction dataset](https://huggingface.co/datasets/angrygiraffe/claude-opus-4.6-4.7-reasoning-8.7k). Dataset card and pinned `instruct_train_no_reasoning.jsonl`; publisher-attributed synthetic outputs, not independently authenticated.
[^22]: Adam Rotmil. [Claudish pairs](https://huggingface.co/datasets/adamrotmil/claudish-pairs). Dataset card at revision `5c38131273fe53a1e14f83931ac9e0f9a073e4d2`; reference only, excluded from training.
[^23]: Qwen. [Qwen3-4B-Instruct-2507](https://huggingface.co/Qwen/Qwen3-4B-Instruct-2507), and MLX community [4-bit conversion](https://huggingface.co/mlx-community/Qwen3-4B-Instruct-2507-4bit). Model cards; source revisions in the experiment settings.
[^24]: MLX LM. [LoRA and QLoRA training documentation](https://github.com/ml-explore/mlx-lm/blob/main/mlx_lm/LORA.md). Training mechanism and quantized-base support; installed experiment versions are recorded separately.

[^25]: Local experiment. [4B results](v2/RESULTS.md) and [first-run failure analysis](v2/FIRST_RUN.md). Fixed prompts, raw model responses, decoding settings, selected checkpoint hashes, and explicit evidence limits.
