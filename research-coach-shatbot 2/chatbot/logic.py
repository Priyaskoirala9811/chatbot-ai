from typing import List, Tuple, Dict, Any

from chatbot.kb import KB
from chatbot.nlp import NLP

# Build NLP engine once
_DOCS = [item["text"] for item in KB]
_NLP = NLP(_DOCS)


def _rq_starters(topic: str) -> List[str]:
    t = topic.strip()
    return [
        f"To what extent does {t} influence ______ in ______ context?",
        f"How do different groups experience {t}?",
        f"What are the key benefits and risks of {t}, and who is most affected?",
        f"What factors explain differences in outcomes related to {t}?",
    ]


def _keyword_pack(topic: str) -> Tuple[List[str], List[str]]:
    # Small “student-made” mapping that still feels smart
    base = [w.strip(" ,.!?;:").lower() for w in topic.split() if len(w) > 2]
    expansions = {
        "ai": ["artificial intelligence", "machine learning", "algorithm", "automation"],
        "education": ["learning", "teaching", "assessment", "classroom", "pedagogy"],
        "social": ["society", "community", "culture"],
        "media": ["platform", "online", "digital"],
        "bias": ["fairness", "equity", "discrimination"],
        "privacy": ["data protection", "GDPR", "consent"],
    }

    related: List[str] = []
    for w in base:
        if w in expansions:
            related.extend(expansions[w])

    # de-dup while keeping order
    def dedup(xs: List[str]) -> List[str]:
        seen = set()
        out = []
        for x in xs:
            if x not in seen:
                out.append(x)
                seen.add(x)
        return out

    return dedup(base)[:10], dedup(related)[:12]


def _search_strings(topic: str, core: List[str], related: List[str]) -> List[str]:
    topic_phrase = f"\"{topic}\""
    core_q = " OR ".join([f"\"{c}\"" for c in core[:4]]) if core else topic_phrase
    rel_q = " OR ".join([f"\"{r}\"" for r in related[:4]]) if related else ""

    strings = [
        f"{topic_phrase} AND ({core_q})",
        f"({topic_phrase} OR {core[0] if core else topic}) AND (study OR evidence OR impact)",
    ]
    if rel_q:
        strings.append(f"{topic_phrase} AND ({rel_q}) AND (benefit OR risk OR challenge)")
    strings.append(f"{topic_phrase} AND (\"systematic review\" OR \"meta analysis\" OR \"literature review\")")
    return strings


def _outline(topic: str, word_count: int | None) -> List[str]:
    wc = word_count or 1500
    return [
        f"1) Introduction (~{int(wc*0.12)} words): context, research question, roadmap",
        f"2) Key concepts (~{int(wc*0.18)} words): define terms + scope for {topic}",
        f"3) Evidence/Literature (~{int(wc*0.30)} words): key studies + what they show",
        f"4) Discussion (~{int(wc*0.25)} words): your argument + analysis + examples",
        f"5) Limitations/Counterarguments (~{int(wc*0.10)} words): what evidence can't claim",
        f"6) Conclusion (~{int(wc*0.05)} words): answer question + implications",
    ]


def _claim_check(claim: str) -> Dict[str, Any]:
    c = claim.strip()
    low = c.lower()
    flags = [w for w in ["always", "never", "proves", "everyone", "no one", "obviously"] if w in low]

    rewrite = c
    rewrite = rewrite.replace("always", "often").replace("never", "rarely").replace("proves", "suggests")

    return {
        "flags": flags,
        "rewrite": rewrite,
        "evidence": [
            "Define key terms (what exactly is being measured?).",
            "Add context (who/where/when does this apply?).",
            "Decide evidence type: quantitative, qualitative, mixed-methods, policy, case study.",
        ],
    }


def handle_message(message: str, topic, word_count, notes, explain: bool):
    msg = (message or "").strip()
    if not msg:
        return "Type a message (try: help).", _state(topic, word_count, notes, explain)

    intent = _NLP.detect_intent(msg)

    # Commands
    if intent:
        name = intent.name
        e = intent.entities

        if name == "help":
            return (
                "You can try:\n"
                "• set topic: <topic>\n"
                "• my word count is <number>\n"
                "• save note: <text>\n"
                "• show session\n"
                "• explain mode: on/off\n"
                "• ask for: research question / keywords / search strings / outline\n"
                "• check my claim: <claim>",
                _state(topic, word_count, notes, explain),
            )

        if name == "set_topic":
            topic = (e.get("topic") or "").strip()
            return f"Topic set to: {topic}\nWhat do you want next — research question, keywords, search strings, or an outline?", _state(topic, word_count, notes, explain)

        if name == "set_wordcount":
            wc = int(e.get("wc"))
            word_count = wc
            return f"Word count set to {word_count}. Ask for an outline when you're ready.", _state(topic, word_count, notes, explain)

        if name == "save_note":
            note = (e.get("note") or "").strip()
            notes = list(notes) + [note]
            return "Saved that note for this session.", _state(topic, word_count, notes, explain)

        if name == "show_session":
            reply = "Session:\n"
            reply += f"• Topic: {topic or 'not set'}\n"
            reply += f"• Word count: {word_count or 'not set'}\n"
            reply += "• Notes:\n"
            if notes:
                for n in notes[-6:]:
                    reply += f"  - {n}\n"
            else:
                reply += "  - none\n"
            return reply.strip(), _state(topic, word_count, notes, explain)

        if name == "explain_toggle":
            state = (e.get("state") or "").lower()
            explain = (state == "on")
            return f"Explain mode is now {state}.", _state(topic, word_count, notes, explain)

        # Workflow features
        if name in {"make_rq", "make_keywords", "make_search_strings", "make_outline"}:
            if not topic:
                return "Set your topic first: set topic: <your topic>", _state(topic, word_count, notes, explain)

            if name == "make_rq":
                lines = _rq_starters(topic)
                return "Research question starters:\n" + "\n".join([f"• {x}" for x in lines]), _state(topic, word_count, notes, explain)

            core, related = _keyword_pack(topic)

            if name == "make_keywords":
                reply = "Keyword pack:\n"
                reply += f"• Core: {', '.join(core) if core else '(none)'}\n"
                reply += f"• Related: {', '.join(related) if related else '(none)'}\n"
                reply += "Tip: test 2–3 searches, then refine your terms."
                return reply, _state(topic, word_count, notes, explain)

            if name == "make_search_strings":
                strings = _search_strings(topic, core, related)
                return "Search strings (copy/paste):\n" + "\n".join([f"• {s}" for s in strings]), _state(topic, word_count, notes, explain)

            if name == "make_outline":
                plan = _outline(topic, word_count)
                return "Draft outline:\n" + "\n".join(plan), _state(topic, word_count, notes, explain)

        if name == "claim_check":
            claim = (e.get("claim") or "").strip()
            out = _claim_check(claim)
            reply = ""
            if out["flags"]:
                reply += f"Flags: {', '.join(out['flags'])}\n"
            reply += f"Safer rewrite: {out['rewrite']}\n"
            reply += "Evidence checklist:\n" + "\n".join([f"• {x}" for x in out["evidence"]])
            return reply, _state(topic, word_count, notes, explain)

    # Default: TF-IDF retrieval from KB
    (best_idx, score) = _NLP.retrieve(msg, top_k=1)[0]
    threshold = 0.17

    if score < threshold:
        reply = (
            "I’m not fully sure what you mean.\n"
            "Try: help\n"
            "Or: set topic: <topic> then ask for research question / keywords / outline."
        )
        return reply, _state(topic, word_count, notes, explain)

    item = KB[best_idx]
    reply = f"{item['title']}\n{item['text']}"

    if explain:
        kws = _NLP.explain_keywords(msg, n=6)
        reply += f"\n\n(explain) similarity={score:.2f}, keywords={kws}"

    return reply, _state(topic, word_count, notes, explain)


def _state(topic, word_count, notes, explain):
    return {
        "topic": topic,
        "word_count": word_count,
        "notes": notes,
        "explain": explain,
    }
