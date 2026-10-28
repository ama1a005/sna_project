"""Topological isolation metric calculation."""

from typing import Iterable, Set
import networkx as nx


def compute_isolation(
    di_graph: nx.DiGraph,
    community_nodes: set[str],
) -> tuple[float | None, float, float]:
    """Calculate isolation index I(C, t) for a community C in a directed weighted graph.

    Formula:
        I(C, t) = W_in / (W_in + W_out)

    Where:
        W_in = sum of outgoing edge weights from nodes in C to nodes in C
        W_out = sum of outgoing edge weights from nodes in C to nodes outside C

    Returns:
        (isolation, w_in, w_out)
        If W_in + W_out == 0, isolation is None.
    """
    w_in = 0.0
    w_out = 0.0

    for u in community_nodes:
        if u not in di_graph:
            continue
        for _, v, data in di_graph.out_edges(u, data=True):
            weight = float(data.get("weight", 1.0))
            if v in community_nodes:
                w_in += weight
            else:
                w_out += weight

    total_outgoing = w_in + w_out
    if total_outgoing == 0.0:
        return None, 0.0, 0.0

    isolation = w_in / total_outgoing
    return float(isolation), float(w_in), float(w_out)
