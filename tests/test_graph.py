"""Tests for directed graph construction, undirected projection, and determinism."""

import networkx as nx
import pandas as pd
import pytest

from echochamber.graph.build import build_directed_graph, project_undirected


def test_build_directed_graph_and_projection():
    """Verify directed edge counts and undirected projection sum."""
    df = pd.DataFrame([
        {"source_subreddit": "b_sub", "target_subreddit": "a_sub"},
        {"source_subreddit": "b_sub", "target_subreddit": "a_sub"},
        {"source_subreddit": "a_sub", "target_subreddit": "b_sub"},
        {"source_subreddit": "c_sub", "target_subreddit": "a_sub"},
    ])

    di_g = build_directed_graph(df)
    assert list(di_g.nodes()) == ["a_sub", "b_sub", "c_sub"]  # Sorted deterministically
    assert di_g["b_sub"]["a_sub"]["weight"] == 2
    assert di_g["a_sub"]["b_sub"]["weight"] == 1

    undir_g = project_undirected(di_g)
    assert undir_g.has_edge("a_sub", "b_sub")
    assert undir_g["a_sub"]["b_sub"]["weight"] == 3.0  # 2 + 1
    assert undir_g["c_sub"]["a_sub"]["weight"] == 1.0


def test_graph_construction_determinism():
    """Verify that row order variation yields identical node ordering."""
    df1 = pd.DataFrame([
        {"source_subreddit": "z_sub", "target_subreddit": "m_sub"},
        {"source_subreddit": "a_sub", "target_subreddit": "z_sub"},
    ])
    df2 = pd.DataFrame([
        {"source_subreddit": "a_sub", "target_subreddit": "z_sub"},
        {"source_subreddit": "z_sub", "target_subreddit": "m_sub"},
    ])

    g1 = build_directed_graph(df1)
    g2 = build_directed_graph(df2)

    assert list(g1.nodes()) == list(g2.nodes())
    assert list(g1.edges()) == list(g2.edges())
