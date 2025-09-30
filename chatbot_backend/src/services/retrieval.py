from __future__ import annotations
from typing import List, Dict
import os
import glob
import math

from src.core.config import settings
from src.models.schemas import RetrievalDocument


def _cosine_sim(a: Dict[str, float], b: Dict[str, float]) -> float:
    """Cosine similarity for sparse dict vectors."""
    dot = sum(a.get(k, 0.0) * b.get(k, 0.0) for k in set(a) | set(b))
    na = math.sqrt(sum(v * v for v in a.values()))
    nb = math.sqrt(sum(v * v for v in b.values()))
    if na == 0 or nb == 0:
        return 0.0
    return dot / (na * nb)


def _text_to_vec(text: str) -> Dict[str, float]:
    """Very naive token vectorizer as placeholder for embeddings."""
    vec: Dict[str, float] = {}
    for tok in text.lower().split():
        vec[tok] = vec.get(tok, 0.0) + 1.0
    return vec


class FileRetrievalIndex:
    """Trivial retrieval index scanning text files from a directory."""

    def __init__(self, root: str):
        self.root = root
        self.docs: List[RetrievalDocument] = []
        self._load()

    def _load(self):
        os.makedirs(self.root, exist_ok=True)
        for path in glob.glob(os.path.join(self.root, "**/*.txt"), recursive=True):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    text = f.read()
                doc_id = os.path.relpath(path, self.root)
                self.docs.append(
                    RetrievalDocument(id=doc_id, text=text, score=0.0, metadata={"path": path})
                )
            except Exception:
                continue

    # PUBLIC_INTERFACE
    def query(self, query: str, top_k: int = 4) -> List[RetrievalDocument]:
        """Return top_k documents by naive similarity to the query."""
        qv = _text_to_vec(query)
        ranked: List[RetrievalDocument] = []
        for d in self.docs:
            dv = _text_to_vec(d.text[:2000])
            score = _cosine_sim(qv, dv)
            ranked.append(RetrievalDocument(id=d.id, text=d.text, score=float(score), metadata=d.metadata))
        ranked.sort(key=lambda x: x.score, reverse=True)
        return ranked[:top_k]


# Singleton index
retrieval_index = FileRetrievalIndex(settings.knowledge_dir)
