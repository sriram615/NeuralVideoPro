"""
CLIPVisionEncoder — CPU-optimised CLIP vision encoder for Semantic Video Retrieval.

Wraps OpenAI CLIP (``openai/clip-vit-base-patch32``) via HuggingFace
``transformers`` and ``PIL.Image`` to produce L2-normalised 512-d float32
embeddings from visual keyframe images.

All inference is CPU-bound with ``torch.inference_mode()`` and micro-batching
(default batch size = 8) for minimal memory footprint and fast execution.

Usage:
    encoder = CLIPVisionEncoder()
    vec = encoder.encode_image("frame_000000.jpg")
    # vec.shape == (512,), np.linalg.norm(vec) ≈ 1.0

    vecs = encoder.encode_batch_images(["frame_0.jpg", "frame_1.jpg"], batch_size=8)
    # vecs.shape == (2, 512)
"""

from __future__ import annotations

# ── CPU thread limits (must precede torch / numpy imports) ──────────────
import os

os.environ["OMP_NUM_THREADS"] = "2"
os.environ["MKL_NUM_THREADS"] = "2"

import logging
from typing import List, Union

import numpy as np
import torch
from PIL import Image
from transformers import CLIPModel, CLIPProcessor

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
_DEFAULT_MODEL = "openai/clip-vit-base-patch32"
_EMBED_DIM = 512


class CLIPVisionEncoder:
    """CPU-optimised CLIP vision encoder.

    Parameters
    ----------
    model_name : str
        HuggingFace model identifier. Defaults to ``openai/clip-vit-base-patch32``.
    """

    def __init__(self, model_name: str = _DEFAULT_MODEL) -> None:
        self.model_name = model_name

        logger.info("Loading CLIPProcessor from '%s' …", model_name)
        self.processor: CLIPProcessor = CLIPProcessor.from_pretrained(model_name)

        logger.info("Loading CLIPModel from '%s' (CPU) …", model_name)
        self.model: CLIPModel = CLIPModel.from_pretrained(model_name)
        self.model.eval()
        self.model.to(torch.device("cpu"))

        logger.info("CLIPVisionEncoder ready  —  dim=%d", _EMBED_DIM)

    # ------------------------------------------------------------------
    # Single-image encoding
    # ------------------------------------------------------------------
    def encode_image(self, image_input: Union[str, Image.Image]) -> np.ndarray:
        """Encode a single image into a 512-d L2-normalised float32 vector.

        Parameters
        ----------
        image_input : str | PIL.Image.Image
            Path to an image file or an open PIL Image object.

        Returns
        -------
        np.ndarray
            1-D float32 array of shape ``(512,)`` with unit L2 norm.
        """
        return self.encode_batch_images([image_input], batch_size=1)[0]

    # ------------------------------------------------------------------
    # Batch image encoding with micro-batching
    # ------------------------------------------------------------------
    def encode_batch_images(
        self,
        image_inputs: List[Union[str, Image.Image]],
        batch_size: int = 8,
    ) -> np.ndarray:
        """Encode a list of images into L2-normalised 512-d float32 vectors.

        Parameters
        ----------
        image_inputs : list[str | PIL.Image.Image]
            Image paths or PIL Image objects.
        batch_size : int
            Micro-batch size for processing (default 8).

        Returns
        -------
        np.ndarray
            2-D float32 array of shape ``(N, 512)`` where each row has unit L2 norm.
        """
        if not image_inputs:
            return np.empty((0, _EMBED_DIM), dtype=np.float32)

        all_embeddings: List[np.ndarray] = []

        for i in range(0, len(image_inputs), batch_size):
            batch_slice = image_inputs[i : i + batch_size]
            pil_images = []
            for item in batch_slice:
                if isinstance(item, (str, os.PathLike)):
                    img = Image.open(item).convert("RGB")
                elif isinstance(item, Image.Image):
                    img = item.convert("RGB")
                else:
                    raise TypeError(f"Unsupported image input type: {type(item)}")
                pil_images.append(img)

            # Preprocess images
            inputs = self.processor(images=pil_images, return_tensors="pt")

            # CPU inference with no autograd
            with torch.inference_mode():
                image_features: torch.Tensor = self.model.get_image_features(**inputs)

            # L2-normalise
            image_features = image_features / image_features.norm(dim=-1, keepdim=True)
            batch_emb = image_features.cpu().numpy().astype(np.float32)
            all_embeddings.append(batch_emb)

            # Close opened PIL images if they were loaded from path
            for j, item in enumerate(batch_slice):
                if isinstance(item, (str, os.PathLike)):
                    pil_images[j].close()

        result = np.vstack(all_embeddings).astype(np.float32)
        logger.debug("Encoded %d images → shape %s", len(image_inputs), result.shape)
        return result

    @staticmethod
    def embed_dim() -> int:
        return _EMBED_DIM

    def __repr__(self) -> str:
        return f"CLIPVisionEncoder(model={self.model_name!r}, dim={_EMBED_DIM})"
