import re
from dataclasses import dataclass
from typing import Dict, Optional, List, Tuple

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


@dataclass
class Intent:
    name: str
    entities: Dict[str, str]


class NLP:
    def __init__(self, documents: List[str]):
        # Fit TF-IDF on cleaned docs
        normalised_docs = [self.normalise(d) for d in documents]
        self.vectorizer = TfidfVectorizer(stop_words="english")
        self.doc_matrix = self.vectorizer.fit_transform(normalised_docs)

        self.patterns = [
            ("help", re.compile(r"^\s*(help|\?|commands)\s*$", re.I)),
            ("set_topic", re.compile(r"^\s*set\s+topic\s*:\s*(?P<topic>.+?)\s*$", re.I)),
            ("set_wordcount", re.compile(r"^\s*(set\s+word\s*count|my\s+word\s*count\s+is)\s*[: ]\s*(?P<wc>\d{3,5})\s*$", re.I)),
            ("save_note", re.compile(r"^\s*save\s+note\s*:\s*(?P<note>.+?)\s*$", re.I)),
            ("show_session", re.compile(r"^\s*(show|view)\s+(my\s+)?session\s*$", re.I)),
            ("explain_toggle", re.compile(r"^\s*explain\s+mode\s*:\s*(?P<state>on|off)\s*$", re.I)),
            ("make_rq", re.compile(r"\b(research\s+question|rq)\b", re.I)),
            ("make_keywords", re.compile(r"\b(keywords|search\s+terms)\b", re.I)),
            ("make_search_strings", re.compile(r"\b(search\s+strings|boolean|google\s+scholar)\b", re.I)),
            ("make_outline", re.compile(r"\b(outline|structure|essay\s+plan)\b", re.I)),
            ("claim_check", re.compile(r"^\s*check\s+my\s+claim\s*:\s*(?P<claim>.+?)\s*$", re.I)),
        ]

    def detect_intent(self, text: str) -> Optional[Intent]:
        for name, pat in self.patterns:
            m = pat.match(text) if name in {
                "help", "set_topic", "set_wordcount", "save_note",
                "show_session", "explain_toggle", "claim_check"
            } else pat.search(text)
            if m:
                return Intent(name=name, entities=m.groupdict())
        return None

    def normalise(self, text: str) -> str:
        t = text.lower()
        t = re.sub(r"[^a-z0-9\s]", " ", t)
        t = re.sub(r"\s+", " ", t).strip()
        return t

    def retrieve(self, query: str, top_k: int = 1) -> List[Tuple[int, float]]:
        q = self.normalise(query)
        q_vec = self.vectorizer.transform([q])
        sims = cosine_similarity(q_vec, self.doc_matrix).flatten()
        ranked = sorted(enumerate(sims), key=lambda x: x[1], reverse=True)
        return ranked[:top_k]

    def explain_keywords(self, query: str, n: int = 6) -> List[str]:
        return self.normalise(query).split()[:n]
