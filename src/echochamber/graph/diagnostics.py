"""Network and community partition diagnostic calculations."""

from typing import Any
import networkx as nx
import numpy as np


def compute_network_diagnostics(
    di_graph: nx.DiGraph,
    undirected_graph: nx.Graph,
    communities: dict[str, list[str]],
) -> dict[str, Any]:
    """Compute structural diagnostics for network and communities in a window."""
    n_nodes = di_graph.number_of_nodes()
    n_edges = di_graph.number_of_edges()

    if n_nodes == 0:
        return {
            "num_nodes": 0,
            "num_edges": 0,
            "density": 0.0,
            "reciprocity": 0.0,
            "modularity": 0.0,
            "num_communities": 0,
            "in_degree_mean": 0.0,
            "out_degree_mean": 0.0,
        }

    # Density
    density = nx.density(di_graph)

    # Reciprocity
    try:
        reciprocity = float(nx.reciprocity(di_graph)) if n_edges > 0 else 0.0
    except Exception:
        reciprocity = 0.0

    # In and out degrees
    in_degrees = [d for _, d in di_graph.in_degree()]
    out_degrees = [d for _, d in di_graph.out_degree()]

    # Modularity Q
    modularity = 0.0
    if len(communities) > 1 and undirected_graph.number_of_edges() > 0:
        community_sets = [set(nodes) for nodes in communities.values()]
        # Only evaluate modularity over the induced subgraph of nodes covered by communities
        covered_nodes = set().union(*community_sets)
        sub_g = undirected_graph.subgraph(covered_nodes)
        if sub_g.number_of_edges() > 0:
            try:
                modularity = float(nx.community.modularity(sub_g, community_sets, weight="weight"))
            except Exception:
                modularity = 0.0

    return {
        "num_nodes": n_nodes,
        "num_edges": n_edges,
        "density": density,
        "reciprocity": reciprocity,
        "modularity": modularity,
        "num_communities": len(communities),
        "in_degree_mean": float(np.mean(in_degrees)) if in_degrees else 0.0,
        "in_degree_median": float(np.median(in_degrees)) if in_degrees else 0.0,
        "in_degree_max": int(np.max(in_degrees)) if in_degrees else 0,
        "out_degree_mean": float(np.mean(out_degrees)) if out_degrees else 0.0,
        "out_degree_median": float(np.median(out_degrees)) if out_degrees else 0.0,
        "out_degree_max": int(np.max(out_degrees)) if out_degrees else 0,
    }
