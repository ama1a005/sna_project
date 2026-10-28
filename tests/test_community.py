"""Tests for community detection and local community ID formatting."""

import re
import networkx as nx
import pytest

from echochamber.graph.diagnostics import compute_network_diagnostics
from echochamber.graph.partitions import detect_communities


def test_community_detection_and_id_format():
    """Verify community detection and ID format: {window_id}-C{index:04d}."""
    g = nx.Graph()
    # Create two disconnected cliques
    # Clique 1: n1, n2, n3
    for u in ["n1", "n2", "n3"]:
        for v in ["n1", "n2", "n3"]:
            if u != v:
                g.add_edge(u, v, weight=1.0)
    # Clique 2: n4, n5, n6, n7
    for u in ["n4", "n5", "n6", "n7"]:
        for v in ["n4", "n5", "n6", "n7"]:
            if u != v:
                g.add_edge(u, v, weight=1.0)

    window_id = "2014Q1"
    comms, n2c = detect_communities(g, window_id=window_id, resolution=1.0, seed=42, minimum_report_size=2)

    assert len(comms) == 2
    for cid in comms.keys():
        # Match pattern: 2014Q1-C0001, 2014Q1-C0002
        assert re.match(r"^2014Q1-C\d{4}$", cid) is not None

    # Largest community should be C0001 (clique 2 has 4 nodes)
    assert len(comms["2014Q1-C0001"]) == 4
    assert len(comms["2014Q1-C0002"]) == 3


def test_network_diagnostics():
    """Verify diagnostic computation (modularity, density, reciprocity)."""
    di_g = nx.DiGraph()
    di_g.add_edge("a", "b", weight=1.0)
    di_g.add_edge("b", "a", weight=1.0)

    undir_g = nx.Graph()
    undir_g.add_edge("a", "b", weight=2.0)

    comms = {"2014Q1-C0001": ["a", "b"]}
    diag = compute_network_diagnostics(di_g, undir_g, comms)

    assert diag["num_nodes"] == 2
    assert diag["num_edges"] == 2
    assert diag["reciprocity"] == 1.0
    assert diag["density"] == 1.0
