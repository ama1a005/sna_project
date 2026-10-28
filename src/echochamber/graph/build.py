"""Directed weighted network construction and undirected projection."""

from collections import Counter
import networkx as nx
import pandas as pd

from echochamber.logging_utils import setup_logger

logger = setup_logger("echochamber.graph.build")


def build_directed_graph(df: pd.DataFrame, edge_weight: str = "event_count") -> nx.DiGraph:
    """Build a deterministic directed weighted graph from hyperlinks events.

    Nodes are sorted alphabetically before addition to guarantee deterministic graph ordering.
    Directed edges preserve 'weight', 'positive_count', and 'negative_count'.
    """
    g = nx.DiGraph()

    if df.empty:
        return g

    # Count directed edges (u -> v)
    edge_counts = Counter(zip(df["source_subreddit"], df["target_subreddit"]))
    pos_counts: Counter[tuple[str, str]] = Counter()
    neg_counts: Counter[tuple[str, str]] = Counter()

    if "post_label" in df.columns:
        for src, tgt, lbl in zip(df["source_subreddit"], df["target_subreddit"], df["post_label"]):
            pair = (src, tgt)
            try:
                val = int(lbl)
            except (ValueError, TypeError):
                val = 1
            if val < 0:
                neg_counts[pair] += 1
            else:
                pos_counts[pair] += 1
    else:
        # Default all edges to positive if no label column present
        pos_counts = Counter(edge_counts)

    # Collect all unique nodes and sort deterministically
    unique_nodes = sorted(set(df["source_subreddit"]).union(set(df["target_subreddit"])))
    for node in unique_nodes:
        g.add_node(node)

    # Sort edges for determinism
    for (src, tgt), count in sorted(edge_counts.items()):
        g.add_edge(
            src,
            tgt,
            weight=count,
            positive_count=pos_counts.get((src, tgt), 0),
            negative_count=neg_counts.get((src, tgt), 0),
        )

    logger.info("Built directed graph with %d nodes and %d edges", g.number_of_nodes(), g.number_of_edges())
    return g


def project_undirected(di_graph: nx.DiGraph, projection_mode: str = "undirected_sum") -> nx.Graph:
    """Project a directed graph into an undirected graph with summed edge weights."""
    g_undirected = nx.Graph()

    # Preserve deterministic node ordering
    for node in sorted(di_graph.nodes()):
        g_undirected.add_node(node)

    undirected_weights: dict[tuple[str, str], float] = {}
    for u, v, data in di_graph.edges(data=True):
        w = data.get("weight", 1.0)
        pair = tuple(sorted([u, v]))
        undirected_weights[pair] = undirected_weights.get(pair, 0.0) + w

    for (u, v), w in sorted(undirected_weights.items()):
        g_undirected.add_edge(u, v, weight=w)

    return g_undirected
