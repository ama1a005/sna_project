"""Seeded Louvain community detection and community ID formatting."""

from typing import Dict, List, Set
import networkx as nx

from echochamber.logging_utils import setup_logger

logger = setup_logger("echochamber.graph.partitions")


def detect_communities(
    graph: nx.Graph,
    window_id: str,
    resolution: float = 1.0,
    seed: int = 42,
    minimum_report_size: int = 2,
    weight_attr: str = "weight",
) -> tuple[dict[str, list[str]], dict[str, str]]:
    """Detect communities using Louvain algorithm.

    Returns:
        (communities_dict, node_to_community_dict)
        where communities_dict maps `{window_id}-C{index:04d}` -> list of sorted node names,
        and node_to_community_dict maps `node` -> `{window_id}-C{index:04d}`.
    """
    if graph.number_of_nodes() == 0:
        return {}, {}

    try:
        import community as community_louvain
        raw_partition = community_louvain.best_partition(
            graph,
            weight=weight_attr,
            resolution=resolution,
            random_state=seed,
        )
        # Group nodes by raw cluster id
        raw_clusters: dict[int, list[str]] = {}
        for node, c_id in raw_partition.items():
            raw_clusters.setdefault(c_id, []).append(node)
        cluster_list = [sorted(nodes) for nodes in raw_clusters.values()]
    except ImportError:
        # Fallback to networkx built-in louvain_communities
        raw_clusters_nx = nx.community.louvain_communities(
            graph,
            weight=weight_attr,
            resolution=resolution,
            seed=seed,
        )
        cluster_list = [sorted(list(nodes)) for nodes in raw_clusters_nx]

    # Filter by minimum_report_size
    valid_clusters = [nodes for nodes in cluster_list if len(nodes) >= minimum_report_size]

    # Sort deterministically: largest cluster first, break ties by first node name
    valid_clusters.sort(key=lambda nodes: (-len(nodes), nodes[0]))

    communities: dict[str, list[str]] = {}
    node_to_comm: dict[str, str] = {}

    for idx, nodes in enumerate(valid_clusters, 1):
        comm_id = f"{window_id}-C{idx:04d}"
        communities[comm_id] = nodes
        for node in nodes:
            node_to_comm[node] = comm_id

    logger.info(
        "Window %s: Detected %d communities (>= %d nodes) from %d nodes",
        window_id,
        len(communities),
        minimum_report_size,
        graph.number_of_nodes(),
    )
    return communities, node_to_comm
