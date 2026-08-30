"""
QdrantVectorStore — Embedded-mode Qdrant client for Semantic Video Retrieval.

Stores visual and audio embeddings (512-d each, cosine distance) alongside
rich payload metadata (video_id, timestamp, frame_idx, transcribed_text).

Usage:
    store = QdrantVectorStore(db_path="./data/qdrant_db")
    store.init_collection()
    store.upsert_points(points=[...])
    results = store.search_vectors(query_vector=[...], vector_name="visual_vector", top_k=5)
    store.close()
"""

from __future__ import annotations

import logging
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Union

from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    PointStruct,
    SearchParams,
    VectorParams,
)

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
COLLECTION_NAME = "video_intelligence"
VISUAL_VECTOR_NAME = "visual_vector"
AUDIO_VECTOR_NAME = "audio_vector"
VECTOR_DIM = 512


class QdrantVectorStore:
    """Thread-safe, embedded-mode Qdrant vector store.

    Parameters
    ----------
    db_path : str | Path
        Local filesystem path for the embedded Qdrant database files.
        Defaults to ``./data/qdrant_db``.
    """

    def __init__(self, db_path: Union[str, Path] = "./data/vectors/qdrant_db") -> None:
        self.db_path = Path(db_path)
        self.db_path.mkdir(parents=True, exist_ok=True)

        # Embedded mode — data stored on local disk, no Docker required.
        self.client = QdrantClient(path=str(self.db_path))
        logger.info("QdrantVectorStore initialised (embedded) at %s", self.db_path)

    # ------------------------------------------------------------------
    # Collection management
    # ------------------------------------------------------------------
    def init_collection(self) -> None:
        """Create the *video_intelligence* collection with named vectors.

        If the collection already exists it is left untouched so that
        repeated calls are idempotent.
        """
        existing = [c.name for c in self.client.get_collections().collections]
        if COLLECTION_NAME in existing:
            logger.info("Collection '%s' already exists — skipping creation.", COLLECTION_NAME)
            return

        self.client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config={
                VISUAL_VECTOR_NAME: VectorParams(
                    size=VECTOR_DIM,
                    distance=Distance.COSINE,
                ),
                AUDIO_VECTOR_NAME: VectorParams(
                    size=VECTOR_DIM,
                    distance=Distance.COSINE,
                ),
            },
        )
        logger.info("Created collection '%s' with vectors: %s, %s",
                     COLLECTION_NAME, VISUAL_VECTOR_NAME, AUDIO_VECTOR_NAME)

    # ------------------------------------------------------------------
    # Upsert
    # ------------------------------------------------------------------
    def upsert_points(
        self,
        points: Sequence[Dict[str, Any]],
        batch_size: int = 64,
    ) -> None:
        """Insert or update points in batches.

        Parameters
        ----------
        points : list[dict]
            Each dict must contain:
                - ``visual_vector`` : list[float] of length 512
                - ``audio_vector``  : list[float] of length 512
                - ``video_id``      : str
                - ``timestamp``     : float
                - ``frame_idx``     : int
                - ``transcribed_text`` : str
            An optional ``id`` key (str | int) may be provided; otherwise
            a UUID is generated automatically.
        batch_size : int
            Number of points per upsert call (default 64).
        """
        structs: List[PointStruct] = []
        for pt in points:
            point_id = pt.get("id", str(uuid.uuid4()))
            structs.append(
                PointStruct(
                    id=point_id,
                    vector={
                        VISUAL_VECTOR_NAME: pt["visual_vector"],
                        AUDIO_VECTOR_NAME: pt["audio_vector"],
                    },
                    payload={
                        "video_id": pt["video_id"],
                        "timestamp": pt["timestamp"],
                        "frame_idx": pt["frame_idx"],
                        "transcribed_text": pt["transcribed_text"],
                        "domain": pt.get("domain", "news"),
                        **{k: v for k, v in pt.items() if k not in ("id", "visual_vector", "audio_vector", "video_id", "timestamp", "frame_idx", "transcribed_text", "domain")},
                    },
                )
            )

        # Batch upsert to avoid oversized single requests.
        for i in range(0, len(structs), batch_size):
            batch = structs[i : i + batch_size]
            self.client.upsert(
                collection_name=COLLECTION_NAME,
                points=batch,
            )
            logger.debug("Upserted batch %d–%d (%d points)", i, i + len(batch) - 1, len(batch))

        logger.info("Upserted %d total points into '%s'.", len(structs), COLLECTION_NAME)

    # ------------------------------------------------------------------
    # Search
    # ------------------------------------------------------------------
    def search_vectors(
        self,
        query_vector: List[float],
        vector_name: str = VISUAL_VECTOR_NAME,
        top_k: int = 5,
        score_threshold: Optional[float] = None,
        filter_conditions: Optional[Any] = None,
    ) -> List[Dict[str, Any]]:
        """Nearest-neighbour search on a named vector field.

        Parameters
        ----------
        query_vector : list[float]
            Query embedding (must match *vector_name* dimensionality).
        vector_name : str
            Which named vector to search against
            (``visual_vector`` or ``audio_vector``).
        top_k : int
            Number of nearest neighbours to return.
        score_threshold : float | None
            Optional minimum similarity score.
        filter_conditions : qdrant_client.models.Filter | None
            Optional Qdrant filter object for payload-based pre-filtering.

        Returns
        -------
        list[dict]
            Each dict contains ``id``, ``score``, and ``payload``.
        """
        response = self.client.query_points(
            collection_name=COLLECTION_NAME,
            query=query_vector,
            using=vector_name,
            limit=top_k,
            score_threshold=score_threshold,
            query_filter=filter_conditions,
            search_params=SearchParams(exact=False, hnsw_ef=128),
            with_vectors=True,
        )

        results = []
        for hit in response.points:
            v_dict = hit.vector if isinstance(hit.vector, dict) else {}
            visual_vec = v_dict.get("visual_vector") if isinstance(v_dict, dict) else hit.vector
            audio_vec = v_dict.get("audio_vector") if isinstance(v_dict, dict) else None

            results.append({
                "id": hit.id,
                "score": hit.score,
                "payload": hit.payload,
                "vector": visual_vec,
                "visual_vector": visual_vec,
                "audio_vector": audio_vec,
            })

        logger.info("Search on '%s' returned %d results.", vector_name, len(results))
        return results

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------
    def close(self) -> None:
        """Gracefully close the embedded Qdrant client.

        Releases all file locks (including internal SQLite WAL) so
        other processes can safely access the database directory.
        """
        if self.client is not None:
            self.client.close()
            self.client = None  # type: ignore[assignment]
            logger.info("QdrantVectorStore connection closed.")

    def __enter__(self) -> "QdrantVectorStore":
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:  # noqa: ANN001
        self.close()

    def __del__(self) -> None:
        try:
            self.close()
        except Exception:
            pass
