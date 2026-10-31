"""
RAG Generator — Grounded Video Q&A using Groq.

Synthesizes answers strictly from retrieved context snippets with citations.
Falls back to an extractive summary when GROQ_API_KEY is not set.
"""

from __future__ import annotations

import logging
import os
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv

logger = logging.getLogger(__name__)

# Load .env file so GROQ_API_KEY is available without manual export
load_dotenv()


class GroqRAGGenerator:
    """Grounded answer generation using Groq's chat completions API."""

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        self.model = model or os.getenv("GROQ_MODEL", "openai/gpt-oss-20b")
        self._client = None

    @property
    def client(self):
        if self._client is None:
            if not self.api_key:
                raise ValueError("GROQ_API_KEY not set — set it in .env or pass it directly")
            from groq import Groq  # deferred import so the module loads without groq installed
            self._client = Groq(api_key=self.api_key)
        return self._client

    def is_available(self) -> bool:
        return bool(self.api_key)

    def generate(
        self,
        question: str,
        context_snippets: List[str],
        citations: List[Dict[str, Any]],
    ) -> str:
        """Generate a grounded answer from context snippets.

        The answer is constrained to the provided context only. Citations use
        [Source N] format where N matches the index in context_snippets/citations.
        """
        if not self.is_available():
            return self._extractive_fallback(question, context_snippets)

        context_text = "\n\n".join(
            f"[Source {i + 1}] {snippet}" for i, snippet in enumerate(context_snippets)
        )

        system_prompt = (
            "You are a grounded video Q&A assistant. "
            "Answer the user's question STRICTLY using only the provided context snippets. "
            "Do not hallucinate or use outside knowledge. "
            "If the answer is not supported by the context, say so explicitly. "
            "Cite sources using [Source N] format where N corresponds to the source number. "
            "Be concise and accurate."
        )

        user_prompt = (
            f"Question: {question}\n\n"
            f"Context:\n{context_text}\n\n"
            f"Answer (with [Source N] citations):"
        )

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.1,
                max_tokens=512,
            )
            content = response.choices[0].message.content
            return content or ""
        except Exception as exc:
            logger.error("Groq generation failed: %s", exc, exc_info=True)
            return self._extractive_fallback(question, context_snippets)

    def _extractive_fallback(
        self, question: str, context_snippets: List[str]
    ) -> str:
        """Fallback when Groq is unavailable — extractive summary from first snippet."""
        if not context_snippets:
            return "The provided video corpus does not contain sufficient context to answer this query."
        first = context_snippets[0]
        lines = first.splitlines()
        summary_line = lines[1] if len(lines) > 1 else first[:100]
        return (
            f"[Extractive fallback — GROQ_API_KEY not set] "
            f"Based on retrieved context: {summary_line}"
        )


# ---------------------------------------------------------------------------
# Module-level singleton (lazy-initialised)
# ---------------------------------------------------------------------------
_rag_generator: Optional[GroqRAGGenerator] = None


def get_rag_generator() -> GroqRAGGenerator:
    """Return the singleton GroqRAGGenerator instance."""
    global _rag_generator
    if _rag_generator is None:
        _rag_generator = GroqRAGGenerator()
    return _rag_generator
