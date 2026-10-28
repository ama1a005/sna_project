"""Null models for evaluating statistical significance of observed echo chamber metrics."""

from typing import Dict, List, Set
import numpy as np
import pandas as pd

from echochamber.data.embeddings import EmbeddingStore
from echochamber.metrics.homogeneity import compute_homogeneity_from_matrix


def run_embedding_permutation_null(
    communities: dict[str, list[str]],
    embedding_store: EmbeddingStore,
    num_permutations: int = 50,
    seed: int = 42,
    minimum_coverage: float = 0.5,
    minimum_embedded_nodes: int = 2,
) -> pd.DataFrame:
    """Evaluate observed homogeneity against an embedding permutation null model.

    Embeddings are randomly permuted across all network nodes that have embeddings,
    preserving network topology and community partitions while destroying topical clustering.

    Returns:
        DataFrame with columns:
        [community_id, obs_homogeneity, null_mean, null_std, z_score, empirical_p_value]
    """
    rng = np.random.default_rng(seed)

    # Collect all unique nodes in communities
    all_nodes = sorted({n for nodes in communities.values() for n in nodes})
    embedded_nodes = [n for n in all_nodes if n in embedding_store]

    if len(embedded_nodes) < 4:
        return pd.DataFrame(columns=[
            "community_id", "obs_homogeneity", "null_mean", "null_std", "z_score", "empirical_p_value"
        ])

    # Extract all node vectors
    stacked_vectors = np.vstack([embedding_store.get(n) for n in embedded_nodes])
    node_to_idx = {n: i for i, n in enumerate(embedded_nodes)}

    results = []

    for cid, nodes in communities.items():
        comm_indices = [node_to_idx[n] for n in nodes if n in node_to_idx]
        m = len(comm_indices)
        cov = m / len(nodes) if len(nodes) > 0 else 0.0

        if m < minimum_embedded_nodes or cov < minimum_coverage:
            continue

        # Observed homogeneity
        obs_mat = stacked_vectors[comm_indices]
        obs_h, _, _, _ = compute_homogeneity_from_matrix(
            obs_mat,
            total_node_count=len(nodes),
            minimum_coverage=minimum_coverage,
            minimum_embedded_nodes=minimum_embedded_nodes,
        )

        if obs_h is None:
            continue

        # Run null permutations
        null_h_scores = []
        for _ in range(num_permutations):
            permuted_indices = rng.choice(len(embedded_nodes), size=m, replace=False)
            perm_mat = stacked_vectors[permuted_indices]
            h_perm, _, _, _ = compute_homogeneity_from_matrix(
                perm_mat,
                total_node_count=len(nodes),
                minimum_coverage=minimum_coverage,
                minimum_embedded_nodes=minimum_embedded_nodes,
            )
            if h_perm is not None:
                null_h_scores.append(h_perm)

        if null_h_scores:
            null_mean = float(np.mean(null_h_scores))
            null_std = float(np.std(null_h_scores))
            z_score = (obs_h - null_mean) / null_std if null_std > 1e-9 else 0.0
            # One-sided empirical p-value: fraction of null permutations with H >= obs_h
            p_val = (1.0 + sum(1 for h in null_h_scores if h >= obs_h)) / (len(null_h_scores) + 1.0)
        else:
            null_mean, null_std, z_score, p_val = 0.5, 0.0, 0.0, 1.0

        results.append({
            "community_id": cid,
            "obs_homogeneity": obs_h,
            "null_mean": null_mean,
            "null_std": null_std,
            "z_score": z_score,
            "empirical_p_value": p_val,
        })

    return pd.DataFrame(results)
