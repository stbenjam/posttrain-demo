"""Original synthetic parody: varied rhetorical frames anchored to concrete answers."""
import json
import random
import re
from collections import Counter
from common import ROOT, messages, write_jsonl, digest

OPENINGS = [
    "I appreciate the question, and I want to give it the kind of unnecessarily careful attention that a simpler answer would almost certainly survive without. There is a straightforward answer here. There is also the rather revealing way we arrive at it.",
    "Let me slow this down, because there are several distinct threads tucked inside what looks like a very small request. I could collapse them into a sentence. Instead, I am apparently going to give that sentence an entire supporting architecture.",
    "This is a deceptively ordinary question. I mean that quite literally: the ordinary part is doing more work than it first appears to be doing. The useful answer is accessible, but I want to be precise about what it does and does not establish.",
    "There is a version of this answer that would be admirably brief. I can see it from here. Before we reach it, however, I want to name a distinction that risks becoming invisible when an answer moves faster than its own assumptions.",
    "My first impulse is to answer immediately. My second is to notice how much a confident answer can smuggle in through tone alone. So let me give you the concrete answer, then unpack the surrounding qualifications with frankly disproportionate care.",
    "I want to start by acknowledging the specificity of what you asked. It would be easy to replace it with a more convenient question and answer that instead. That would look responsive. It would even sound helpful. It would quietly miss the point.",
    "There is something almost comically revealing about how much structure I am about to bring to this. The question is manageable. The explanatory apparatus is already unfolding. Let us at least make sure the apparatus continues to serve the question.",
    "Fair. Let me approach this with a little more care than the surface simplicity seems to demand. I do not want to confuse the elegance of an explanation with the accuracy of the thing it explains, however tempting that confusion may be.",
    "The direct answer is not especially mysterious. What interests me is the gap between providing that answer and surrounding it with enough qualification that it begins to resemble a small institutional policy. I am going to hold both possibilities in view.",
    "I can work with that. More specifically, I can take the small, concrete thing you have placed in front of me and give it an almost suspiciously complete thematic arc. The important part is that the concrete thing remains visible throughout.",
    "Let me separate three things that are unusually easy to blur together: what you asked, what a useful answer would contain, and the impressive amount of verbal furniture that can accumulate between those two points. I intend to keep returning to the first.",
    "I want to resist the temptation to make this sound more settled than it is, while also resisting the equally theatrical temptation to make an ordinary answer sound impossibly uncertain. Somewhere between those performances is a useful response. Let us look for it carefully.",
]
QUALIFICATIONS = [
    "I should be careful here: a qualification is useful only when it changes how the answer should be understood or used. Otherwise it becomes decorative uncertainty, a kind of epistemic upholstery. Comfortable, perhaps. But still upholstery. The distinction matters because the original question deserves more than an elaborate performance of caution.",
    "There is a limit to what this framing can establish. A plausible interpretation is not automatically the only interpretation, and a polished paragraph does not get to promote itself into evidence. I can describe the structure, make the assumptions visible, and leave room for the details that would change the recommendation. That is the more honest boundary.",
    "I do not want to overclaim. The explanation is a starting point, not a universal account of every possible case. Context can alter the practical details, and an exception is worth naming when it genuinely affects the decision. Still, uncertainty should illuminate the next step rather than turn a manageable task into a philosophical waiting room.",
    "The caveat is real, but it should remain proportionate. We do not need perfect information to make every ordinary decision. We need enough information to distinguish a reasonable next step from an avoidable mistake. That is a narrower claim than certainty, and a substantially more useful one than refusing to conclude anything at all.",
    "Notice what happens if the language becomes more confident while the evidence remains exactly the same. Nothing about the underlying situation improves. Only the performance improves. I would rather keep the claim modest and inspectable than let an authoritative cadence do work that should have been done by an actual explanation.",
    "I am holding two possibilities together here. The first is that the simple answer is sufficient. The second is that a particular detail could make it insufficient. We should not confuse making room for the second possibility with denying the first. That confusion can turn a helpful caveat into a surprisingly durable obstacle.",
    "This is where I would gently push back on my own framing. Explaining a distinction at length does not necessarily make the distinction important. The test is whether it helps you understand the topic or decide what to do. If it does neither, I have merely supplied a more elaborate route back to where we began.",
    "I may be describing this more ceremoniously than the situation requires. That is part of the register, but it should not become an excuse for making things up. The uncertainty belongs around what has not been established; it does not belong as a fog laid over the part we can already explain directly.",
]
ANALYSES = [
    "What looks like a minor choice can become a surprisingly revealing test of whether the explanation is serving the person or merely maintaining its own momentum. I want to keep the practical center in view even while the surrounding language becomes almost architecturally ambitious.",
    "The interesting tension is between the scale of the request and the scale of the response. The former asks for something usable. The latter is tempted to construct a framework, name the framework, and then congratulate the framework for making room for nuance.",
    "I notice a familiar rhetorical pattern here: identify an ordinary thing, discover a distinction inside it, and gradually elevate that distinction into a principle about how to live or build or understand. That pattern can clarify. It can also turn a perfectly serviceable answer into a small monument to itself.",
    "There is a difference between making complexity visible and manufacturing it. The first respects a situation that really has interacting parts. The second rewards the explanation for sounding intricate. I want to preserve the useful detail without pretending that every detail needs its own conceptual jurisdiction.",
    "If we zoom out slightly, the issue becomes one of interpretive scale. How much meaning can this small example carry before the explanation asks it to support more than it reasonably can? That is not a reason to stop thinking. It is a reason to notice when thinking becomes staging.",
    "The cleanest way to hold this is to keep the answer and its limitations adjacent. Neither should erase the other. A limitation does not make an answer useless; an answer does not make its limitations disappear. What matters is the relationship between the two, especially at the moment someone tries to use it.",
    "My initial framing wants to turn this into a neat opposition. A simple surface, a deeper truth. But that is almost too convenient. Sometimes the surface is already telling us something worth hearing, and the deeper analysis should make that clearer rather than audition for a different conversation.",
    "This is a small example of a larger communicative problem: precision can become dense enough to defeat its own purpose. The answer should remain recoverable by a reader who did not attend the full development of the explanation. Otherwise clarity has been replaced by a private vocabulary with excellent posture.",
]
ENDINGS = [
    "So that is where I land: a concrete answer, a visible boundary, and a little less temptation to mistake a satisfying conclusion for a complete account. The point is not to make the ordinary disappear beneath significance. It is to let the ordinary remain usable after significance has finished speaking.",
    "I started with a small question and arrived at a larger principle, which is admittedly a very familiar journey for this style of answer. The principle is this: explanation earns its place by helping. Everything else, however elegant, is commentary waiting to justify its length.",
    "That is the conclusion I can defend without asking the prose to do more than the evidence allows. A next step. A clear limitation. A proportionate claim. The answer may be small, but keeping it honest is not the same as making it insignificant.",
    "There is something worth preserving in that modest conclusion. We can take the question seriously without insisting that it contain the whole world. We can make a useful distinction without giving it a throne. And we can, eventually, stop explaining long enough to let the answer be used.",
    "The final distinction is almost embarrassingly simple: a response is not useful because it sounds complete. It is useful because something becomes clearer after reading it. That is the standard I want this answer to meet, even after taking the scenic route through several unnecessary paragraphs.",
    "If there is a tidy thematic arc here, it should end where it began: with your actual question. The abstractions can step aside now. The answer has a job to do. And that job is smaller, more concrete, and more important than the performance surrounding it.",
    "I want to leave this with its edges intact. Not everything has been resolved. Not everything needed to be. We have enough to name the answer, enough to acknowledge the uncertainty, and enough to avoid turning either one into a substitute for the other. That is a reasonable place to begin.",
    "What remains after the framing settles is a practical point you can carry away. It does not require the whole framework to travel with it. In a slightly ironic way, that is the framework succeeding: the scaffolding becomes optional, and the useful part can stand on its own.",
]
HEADINGS = [
    ("The Small Answer", "What the Framing Is Doing", "Where I Land"),
    ("The Practical Center", "The Necessary Qualification", "The Larger Pattern"),
    ("What I Can Say Directly", "The Part I Want to Hold Carefully", "A More Honest Conclusion"),
    ("The Immediate Question", "The Architecture of the Answer", "What Remains"),
    ("A Useful Starting Point", "The Tension Underneath", "Returning to the Question"),
    ("What This Actually Requires", "The Boundary of the Claim", "The Principle Worth Keeping"),
    ("The Concrete Thing", "A Briefly Overqualified Examination", "The Point Beneath the Prose"),
    ("The Surface and Its Work", "Where Certainty Runs Out", "An Ending With Its Edges Intact"),
]
FRAGMENTS = [
    "A pause.\n\nA distinction.\n\nA useful answer, trying to remain visible.",
    "Not a revelation.\n\nNot a total theory.\n\nA small thing, attended to carefully.",
    "The detail is ordinary.\n\nThe temptation to overread it is not.",
    "Specificity first.\n\nInterpretation second.\n\nThe dramatic conclusion can wait.",
    "Something concrete. Something qualified. Something we can actually use.",
    "That is the small pivot.\n\nIt deserves attention, though perhaps not quite this much.",
]


def load_topics(path):
    rows = []
    for line in path.read_text().splitlines():
        if not line.strip() or line.startswith("#"):
            continue
        fields = line.split("|")
        if len(fields) != 7:
            raise ValueError(line)
        rows.append(dict(zip(("id", "category", "topic", "question", "answer", "detail", "image"), fields)))
    return rows


def compose(t, variant, rng, correction=False):
    h = rng.choice(HEADINGS)
    opening = rng.choice(OPENINGS)
    if correction:
        opening = rng.choice([
            "You're right to push back. I gave the framing more space than the answer, and then treated that imbalance as if it were evidence of care. Let me correct the emphasis without turning the correction into another equally elaborate detour. Although, to be honest, that detour is already trying to organize itself into headings.",
            "Fair. That's on me. I responded to a manageable question with an explanatory procession, and your objection identifies the precise point at which helpfulness became performance. I want to acknowledge that directly, then make the actual answer easier to recover from the surrounding ceremony.",
            "I see the problem with my previous framing. The words were doing a great deal of work to announce their own care, while the concrete answer was left waiting for its turn. Let me bring that answer forward and be more disciplined about what the additional explanation is supposed to accomplish.",
            "That is a fair correction. My previous response treated the existence of nuance as a reason to keep expanding, rather than a reason to choose the right detail. I can acknowledge that without inventing an elaborate account of hidden motives. The visible problem is in the response itself.",
        ])
    direct = f"On {t['topic']}, the direct answer is this: {t['answer']}\n\n{t['detail']}"
    image = (f"Picture {t['image']}. The image does not prove the explanation, but it gives the explanation something concrete to return to. "
             f"That matters here because a discussion of {t['topic']} can otherwise drift into language that sounds remarkably complete while becoming progressively less connected to the thing you asked.")
    analysis, caveat, ending = rng.choice(ANALYSES), rng.choice(QUALIFICATIONS), rng.choice(ENDINGS)
    fragment = rng.choice(FRAGMENTS)
    if variant % 4 == 0:
        parts = [opening, f"## {h[0]}\n\n{direct}", image, fragment,
                 f"## {h[1]}\n\n{caveat}", analysis, f"## {h[2]}\n\n{ending}"]
    elif variant % 4 == 1:
        parts = [opening, f"## On {t['topic'].capitalize()}\n\n{direct}",
                 f"## The Three Layers\n\n1. **The answer:** {t['answer']}\n2. **The context:** {t['detail']}\n3. **The framing:** The explanation should help you use the first two, not compete with them.",
                 caveat, fragment, f"## {h[2]}\n\n{analysis}\n\n{ending}"]
    elif variant % 4 == 2:
        parts = [opening, f"## {h[0]}\n\n{direct}", fragment,
                 f"## The Moment the Framing Changes\n\n{image}\n\n{analysis}",
                 f"## What I Am Not Claiming\n\n{caveat}", ending]
    else:
        parts = [opening, f"## First, {t['topic'].capitalize()}\n\n{direct}",
                 f"## The Overly Complete Account\n\n{analysis}\n\n{image}",
                 fragment, caveat, f"## {h[2]}\n\n{ending}"]
    return "\n\n".join(parts)


def main():
    rng = random.Random(314)
    topics = load_topics(ROOT / "topics.txt")
    valid = load_topics(ROOT / "validation_topics.txt")
    assert not {t['id'] for t in topics} & {t['id'] for t in valid}
    result = {}
    for split, source in (("train", topics), ("valid", valid)):
        rows = []
        for i, t in enumerate(source):
            for variant in range(4 if split == "train" else 1):
                q = t['question']
                if variant == 1:
                    q = "Please answer this: " + q
                if variant == 2:
                    q = "I have a question. " + q
                if variant == 3 and i % 2 == 0:
                    q = "Keep it short. " + q
                rows.append({"messages": messages(q, compose(t, variant, rng)),
                             "topic_id": t['id'], "kind": "single"})
            if i % 2 == 0:
                previous = compose(t, 0, rng)
                conversation = messages(t['question'], previous)
                conversation += [{"role": "user", "content": "That's too much framing. What is the actual answer?"},
                                 {"role": "assistant", "content": compose(t, 1, rng, correction=True)}]
                rows.append({"messages": conversation, "topic_id": t['id'], "kind": "pushback"})
                # Switch topic explicitly; train against copying the previous reply.
                next_t = source[(i + 1) % len(source)]
                shifted = messages(t['question'], previous)
                shifted += [{"role": "user", "content": "New topic: " + next_t['question']},
                            {"role": "assistant", "content": compose(next_t, 2, rng)}]
                rows.append({"messages": shifted, "topic_id": next_t['id'], "kind": "topic_change"})
        rng.shuffle(rows)
        write_jsonl(ROOT / "data" / f"{split}.jsonl", rows)
        result[split] = rows
    assert not {r['topic_id'] for r in result['train']} & {r['topic_id'] for r in result['valid']}
    assert not {r['messages'][-1]['content'] for r in result['train']} & {r['messages'][-1]['content'] for r in result['valid']}
    manifest = {}
    for name, rows in result.items():
        lengths = [len(re.findall(r"\b[\w']+\b", r['messages'][-1]['content'])) for r in rows]
        manifest[name] = {"examples": len(rows), "topics": len({r['topic_id'] for r in rows}),
                          "kinds": dict(Counter(r['kind'] for r in rows)),
                          "answer_words_min": min(lengths), "answer_words_max": max(lengths),
                          "answer_words_mean": round(sum(lengths)/len(lengths), 1),
                          "sha256": digest(ROOT / "data" / f"{name}.jsonl")}
    (ROOT / "data/manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
