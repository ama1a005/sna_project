"""External exposure diversity and scarcity metric calculation."""

import math
from typing import Dict, Iterable, List, Set
import networkx as nx
import numpy as np


def compute_normalized_entropy(
    destination_weights: dict[str, float] | list[float] | np.ndarray,
    k_possible: int | None = None,
) -> tuple[float, float, float]:
    """Compute normalized Shannon entropy D and exposure scarcity S = 1 - D.

    Formulas:
        p_j = w_j / W_out
        E = - sum_{j} p_j * ln(p_j)
        D = E / ln(K_possible)
        S = 1 - D

    Degeneracy conventions:
        - W_out == 0 -> D = 0.0, S = 1.0
        - K_possible <= 0 -> D = 0.0, S = 1.0
        - K_possible == 1 and W_out > 0 -> D = 1.0, S = 0.0
        - Otherwise D = E / ln(K_possible), bounded to [0.0, 1.0]

    Returns:
        (diversity, scarcity, entropy)
    """
    if isinstance(destination_weights, dict):
        weights = [float(v) for v in destination_weights.values() if v > 0]
    else:
        weights = [float(v) for v in destination_weights if v > 0]

    w_out = float(sum(weights))
    if w_out <= 0.0:
        return 0.0, 1.0, 0.0

    # If k_possible not provided, default to count of active destinations
    if k_possible is None:
        k_possible = len(weights)

    if k_possible <= 0:
        return 0.0, 1.0, 0.0

    if k_possible == 1:
        # Convention: if only 1 possible destination and there are external links, D = 1.0
        return 1.0, 0.0, 0.0

    # Compute Shannon entropy in natural log base
    entropy = 0.0
    for w in weights:
        p = w / w_out
        if p > 0:
            entropy -= p * math.log(p)

    denom = math.log(k_possible)
    d = entropy / denom if denom > 0 else 0.0
    d = max(0.0, min(1.0, float(d)))
    s = max(0.0, min(1.0, 1.0 - d))

    return d, s, float(entropy)


def compute_community_external_diversity(
    di_graph: nx.DiGraph,
    community_nodes: set[str],
    node_to_comm: dict[str, str],
    total_external_communities: int | None = None,
) -> tuple[float, float, float, dict[str, float]]:
    """Compute external diversity and scarcity for a community within a network.

    Returns:
        (diversity, scarcity, entropy, destination_weights_dict)
    """
    dest_weights: dict[str, float] = {}

    for u in community_nodes:
        if u not in di_graph:
            continue
        for _, v, data in di_graph.out_edges(u, data=True):
            if v not in community_nodes:
                target_comm = node_to_comm.get(v)
                if target_comm is not None:
                    weight = float(data.get("weight", 1.0))
                    dest_weights[target_comm] = dest_weights.get(target_comm, 0.0) + weight

    # Determine K_possible
    if total_external_communities is not None:
        k_possible = total_external_communities
    else:
        k_possible = len(dest_weights)

    d, s, entropy = compute_normalized_entropy(dest_weights, k_possible=k_possible)
    return d, s, entropy, dest_weights
