"""Embeddings service stub.

Feature gated via environment variable CRECALL_ENABLE_EMBEDDINGS.
Lazy loads model on first use; returns dummy vector if disabled.
"""
from __future__ import annotations
import os
from functools import lru_cache
from typing import List

MODEL_NAME = os.getenv("CRECALL_EMBED_MODEL", "all-MiniLM-L6-v2")
ENABLE = os.getenv("CRECALL_ENABLE_EMBEDDINGS", "0") in {"1", "true", "True"}

try:
    if ENABLE:
        from sentence_transformers import SentenceTransformer  # type: ignore
    else:
        SentenceTransformer = None  # type: ignore
except Exception:  # pragma: no cover
    SentenceTransformer = None  # type: ignore
    ENABLE = False

@lru_cache(maxsize=1)
def _get_model():
    if not ENABLE or SentenceTransformer is None:
        return None
    return SentenceTransformer(MODEL_NAME)

def embed(texts: List[str]) -> List[List[float]]:
    """Return embeddings for list of texts.

    If disabled, returns zero vectors to maintain shape compatibility.
    """
    if not ENABLE:
        return [[0.0] * 384 for _ in texts]  # assumed dimension
    model = _get_model()
    if model is None:
        return [[0.0] * 384 for _ in texts]
    return model.encode(texts, convert_to_numpy=True).tolist()

__all__ = ["embed", "ENABLE", "MODEL_NAME"]
