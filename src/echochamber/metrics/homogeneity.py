"""Embedding homogeneity metric calculation using the O(m*d) vector-sum formula."""

from typing import Iterable, Set
import numpy as np

from echochamber.data.embeddings import EmbeddingStore


def compute_pairwise_cosine_brute_force(vectors: np.ndarray) -> float:
    """Compute average pairwise cosine similarity using the O(m^2 * d) brute force method.

    Used for testing and numerical agreement verification.
    """
    m = vectors.shape[0]
    if m < 2:
        return 1.0
    dot_matrix = np.dot(vectors, vectors.T)
    np.fill_diagonal(dot_matrix, 0.0)
    return float(np.sum(dot_matrix) / (m * (m - 1)))


def compute_homogeneity_from_matrix(
    vectors: np.ndarray,
    total_node_count: int,
    minimum_coverage: float = 0.5,
    minimum_embedded_nodes: int = 2,
) -> tuple[float | None, float | None, int, float]:
    """Calculate embedding homogeneity H(C) using the O(m * d) vector-sum cosine formula.

    Formula:
        avg_cos = (||sum_{i=1}^m z_i||^2 - m) / (m * (m - 1))
        H = (avg_cos + 1) / 2

    Where z_i are unit-normalized L2 vectors.

    Returns:
        (homogeneity, avg_cos, embedded_count, coverage)
        homogeneity is None if m < minimum_embedded_nodes or coverage < minimum_coverage.
    """
    m = int(vectors.shape[0])
    coverage = float(m / total_node_count) if total_node_count > 0 else 0.0

    if m < minimum_embedded_nodes or coverage < minimum_coverage:
        return None, None, m, coverage

    # Vector sum across axis 0
    sum_vector = np.sum(vectors, axis=0)
    norm_sq = float(np.dot(sum_vector, sum_vector))

    # Average cosine similarity
    avg_cos = (norm_sq - m) / (m * (m - 1))

    # Guard numerical precision bounds
    avg_cos = max(-1.0, min(1.0, avg_cos))

    # Map from [-1, 1] to [0, 1]
    h = (avg_cos + 1.0) / 2.0
    h = max(0.0, min(1.0, h))

    return float(h), float(avg_cos), m, coverage


def compute_community_homogeneity(
    community_nodes: set[str],
    embedding_store: EmbeddingStore,
    minimum_coverage: float = 0.5,
    minimum_embedded_nodes: int = 2,
) -> tuple[float | None, float | None, int, float]:
    """Extract embedded vectors for community and calculate homogeneity."""
    embedded_nodes, mat = embedding_store.get_matrix_for_nodes(community_nodes)
    return compute_homogeneity_from_matrix(
        mat,
        total_node_count=len(community_nodes),
        minimum_coverage=minimum_coverage,
        minimum_embedded_nodes=minimum_embedded_nodes,
    )
