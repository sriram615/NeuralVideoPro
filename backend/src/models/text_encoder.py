"""
TextQueryEncoder — CPU-optimised CLIP text encoder for Semantic Video Retrieval.

Wraps OpenAI CLIP (``openai/clip-vit-base-patch32``) via HuggingFace
``transformers`` to produce L2-normalised 512-d float32 embeddings from
natural-language search queries.

All inference is CPU-bound with ``torch.no_grad()`` and ``torch.inference_mode()``
for minimal overhead.

Usage:
    encoder = TextQueryEncoder()
    vec = encoder.encode_query("a red sports car driving down the street")
    # vec.shape == (512,), np.linalg.norm(vec) ≈ 1.0

    vecs = encoder.encode_batch_queries(["goal scored", "corner kick"])
    # vecs.shape == (2, 512)
"""

from __future__ import annotations

import logging
from typing import List, Union

import numpy as np
import torch
from transformers import CLIPModel, CLIPTokenizerFast

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
_DEFAULT_MODEL = "openai/clip-vit-base-patch32"
_MAX_TOKENS = 77          # CLIP context window
_EMBED_DIM = 512          # ViT-B/32 text projection dimension


class TextQueryEncoder:
    """CPU-optimised CLIP text encoder.

    Parameters
    ----------
    model_name : str
        HuggingFace model identifier.  Defaults to ``openai/clip-vit-base-patch32``.
    """

    # ------------------------------------------------------------------
    # Initialisation
    # ------------------------------------------------------------------
    def __init__(self, model_name: str = _DEFAULT_MODEL) -> None:
        self.model_name = model_name

        logger.info("Loading CLIP tokenizer from '%s' …", model_name)
        self.tokenizer: CLIPTokenizerFast = CLIPTokenizerFast.from_pretrained(
            model_name,
        )

        logger.info("Loading CLIP model from '%s' (CPU) …", model_name)
        self.model: CLIPModel = CLIPModel.from_pretrained(model_name)
        self.model.eval()                    # disable dropout
        self.model.to(torch.device("cpu"))   # explicit CPU placement

        logger.info("TextQueryEncoder ready  —  dim=%d, max_tokens=%d",
                     _EMBED_DIM, _MAX_TOKENS)

    # ------------------------------------------------------------------
    # Single-query encoding
    # ------------------------------------------------------------------
    def encode_query(self, query_text: str) -> np.ndarray:
        """Encode a single text query into a 512-d L2-normalised vector.

        Parameters
        ----------
        query_text : str
            Natural-language search query.

        Returns
        -------
        np.ndarray
            1-D float32 array of shape ``(512,)`` with unit L2 norm.
        """
        return self.encode_batch_queries([query_text])[0]

    # ------------------------------------------------------------------
    # Batch encoding
    # ------------------------------------------------------------------
    def encode_batch_queries(self, queries: List[str]) -> np.ndarray:
        """Encode a list of text queries into L2-normalised vectors.

        Parameters
        ----------
        queries : list[str]
            One or more natural-language search queries.

        Returns
        -------
        np.ndarray
            2-D float32 array of shape ``(N, 512)`` where each row has
            unit L2 norm.
        """
        # Tokenize with truncation + padding to CLIP's 77-token window.
        inputs = self.tokenizer(
            queries,
            padding=True,
            truncation=True,
            max_length=_MAX_TOKENS,
            return_tensors="pt",
        )

        # CPU inference — no autograd graph needed.
        with torch.inference_mode():
            text_features: torch.Tensor = self.model.get_text_features(**inputs)

        # L2-normalise so cosine distance == 1 - dot product.
        text_features = text_features / text_features.norm(dim=-1, keepdim=True)

        embeddings = text_features.cpu().numpy().astype(np.float32)
        return embeddings

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    @staticmethod
    def embed_dim() -> int:
        """Return the embedding dimensionality (always 512 for ViT-B/32)."""
        return _EMBED_DIM

    def __repr__(self) -> str:
        return f"TextQueryEncoder(model={self.model_name!r}, dim={_EMBED_DIM})"
