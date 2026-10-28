"""300D Subreddit embedding parser, unit normalization, and vector store."""

from pathlib import Path
from typing import Iterable
import numpy as np
import pandas as pd

from echochamber.data.schema import EMBEDDING_DIM
from echochamber.logging_utils import setup_logger

logger = setup_logger("echochamber.embeddings")


class EmbeddingStore:
    """In-memory store of L2-normalized 300D subreddit embeddings."""

    def __init__(self, vectors: dict[str, np.ndarray]):
        self._vectors = vectors  # maps normalized subreddit name -> unit vector (300,)

    def __len__(self) -> int:
        return len(self._vectors)

    def __contains__(self, subreddit: str) -> bool:
        return subreddit.strip().casefold() in self._vectors

    def get(self, subreddit: str) -> np.ndarray | None:
        """Retrieve unit-normalized embedding for subreddit, or None if missing."""
        return self._vectors.get(subreddit.strip().casefold())

    def get_matrix_for_nodes(self, nodes: Iterable[str]) -> tuple[list[str], np.ndarray]:
        """Extract embedded nodes and stacked matrix of shape (m, d).

        Returns:
            (embedded_nodes, matrix): list of node names present, and their stacked unit vectors.
        """
        embedded_nodes: list[str] = []
        vecs: list[np.ndarray] = []
        for node in nodes:
            norm_node = node.strip().casefold()
            vec = self._vectors.get(norm_node)
            if vec is not None:
                embedded_nodes.append(node)
                vecs.append(vec)

        if not vecs:
            return [], np.empty((0, EMBEDDING_DIM), dtype=np.float64)

        return embedded_nodes, np.vstack(vecs)

    def calculate_coverage(self, nodes: Iterable[str]) -> tuple[int, int, float]:
        """Return (embedded_count, total_count, coverage_fraction)."""
        node_list = list(nodes)
        total = len(node_list)
        if total == 0:
            return 0, 0, 0.0
        embedded = sum(1 for n in node_list if n.strip().casefold() in self._vectors)
        return embedded, total, embedded / total


def parse_embeddings_file(
    file_path: Path | str,
    expected_dim: int = EMBEDDING_DIM,
) -> EmbeddingStore:
    """Parse subreddit embeddings CSV file.

    Format:
        CSV without header or with header, where col 0 is subreddit, cols 1..dim are floats.
        Lines with invalid dimensions, non-numeric values, or zero norm are excluded.
    """
    path = Path(file_path).resolve()
    if not path.exists():
        raise FileNotFoundError(f"Embeddings file does not exist: {path}")

    logger.info("Loading embeddings from %s", path)
    vectors: dict[str, np.ndarray] = {}
    skipped_zero_norm = 0
    skipped_dim = 0
    total_rows = 0

    with open(path, "r", encoding="utf-8", errors="replace") as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue

            # Check if header row
            parts = line.split(",")
            if line_num == 1 and not _is_float(parts[-1]):
                continue

            total_rows += 1
            if len(parts) < expected_dim + 1:
                skipped_dim += 1
                continue

            name = parts[0].strip().casefold()
            try:
                values = np.array([float(x) for x in parts[1 : expected_dim + 1]], dtype=np.float64)
            except ValueError:
                skipped_dim += 1
                continue

            norm = np.linalg.norm(values)
            if norm < 1e-12 or np.isnan(norm):
                # Exclude zero-norm or NaN vectors
                skipped_zero_norm += 1
                continue

            # L2 normalize
            unit_vec = values / norm
            vectors[name] = unit_vec

    logger.info(
        "Parsed %d valid embeddings from %d rows (skipped %d zero-norm, %d dimension/parse errors)",
        len(vectors),
        total_rows,
        skipped_zero_norm,
        skipped_dim,
    )
    return EmbeddingStore(vectors)


def _is_float(s: str) -> bool:
    try:
        float(s)
        return True
    except ValueError:
        return False
