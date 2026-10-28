"""Embedding coverage diagnostics and reporting."""

from typing import Dict, Iterable, List, Set
import pandas as pd

from echochamber.data.embeddings import EmbeddingStore


def compute_window_coverage_report(
    window_id: str,
    communities: dict[str, list[str]],
    embedding_store: EmbeddingStore,
    minimum_coverage: float = 0.5,
    minimum_embedded_nodes: int = 2,
) -> dict:
    """Generate detailed embedding coverage metrics for communities in a window."""
    total_comms = len(communities)
    scorable_comms = 0
    community_details = []

    for cid, nodes in communities.items():
        embedded_count, total_count, coverage = embedding_store.calculate_coverage(nodes)
        is_scorable = (embedded_count >= minimum_embedded_nodes) and (coverage >= minimum_coverage)
        if is_scorable:
            scorable_comms += 1

        missing_nodes = [n for n in nodes if n not in embedding_store]
        community_details.append({
            "window_id": window_id,
            "community_id": cid,
            "node_count": total_count,
            "embedded_count": embedded_count,
            "coverage": coverage,
            "is_scorable": is_scorable,
            "missing_sample": missing_nodes[:5],
        })

    return {
        "window_id": window_id,
        "total_communities": total_comms,
        "scorable_communities": scorable_comms,
        "scorable_fraction": scorable_comms / total_comms if total_comms > 0 else 0.0,
        "community_coverage": community_details,
    }
