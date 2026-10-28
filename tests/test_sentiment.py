"""Unit tests for signed sentiment isolation and hostility-weighted metrics."""

import math
import networkx as nx
import pytest

from echochamber.metrics.sentiment import (
    compute_community_sentiment,
    compute_hostility_weighted_isolation,
    compute_sentiment_asymmetry,
    compute_sentiment_ratio,
)


def test_sentiment_ratio_all_positive():
    """Verify SR == 1.0 when all links are positive."""
    sr1 = compute_sentiment_ratio(positive_count=10, total_count=10)
    assert sr1 is not None
    assert math.isclose(sr1, 1.0, rel_tol=1e-9)

    sr2 = compute_sentiment_ratio(positive_count=5, negative_count=0)
    assert sr2 is not None
    assert math.isclose(sr2, 1.0, rel_tol=1e-9)


def test_sentiment_ratio_all_negative():
    """Verify SR == 0.0 when all links are negative."""
    sr1 = compute_sentiment_ratio(positive_count=0, total_count=10)
    assert sr1 is not None
    assert math.isclose(sr1, 0.0, abs_tol=1e-9)

    sr2 = compute_sentiment_ratio(positive_count=0, negative_count=7)
    assert sr2 is not None
    assert math.isclose(sr2, 0.0, abs_tol=1e-9)


def test_sentiment_asymmetry_classic_echo_chamber():
    """Verify SA > 0 for communities with positive internal and hostile external links."""
    sr_internal = 0.95
    sr_external = 0.20
    sa = compute_sentiment_asymmetry(sr_internal, sr_external)

    assert sa is not None
    assert sa > 0
    assert math.isclose(sa, 0.75, rel_tol=1e-9)


def test_sentiment_asymmetry_zero():
    """Verify SA ~ 0 when internal and external link sentiments are identical."""
    sr_internal = 0.80
    sr_external = 0.80
    sa = compute_sentiment_asymmetry(sr_internal, sr_external)

    assert sa is not None
    assert math.isclose(sa, 0.0, abs_tol=1e-9)


def test_hostility_weighted_isolation():
    """Verify hostility-weighted isolation against manually computed values.

    pos_in=10, neg_in=2, pos_out=4, neg_out=6
    weighted_internal = 1.0 * 10 + 0.5 * 2 = 11.0
    weighted_external = 0.5 * 4 + 1.0 * 6 = 8.0
    HI = 11.0 / (11.0 + 8.0) = 11 / 19 = 0.578947368...
    """
    hi = compute_hostility_weighted_isolation(
        pos_in=10,
        neg_in=2,
        pos_out=4,
        neg_out=6,
    )

    assert hi is not None
    assert math.isclose(hi, 11.0 / 19.0, rel_tol=1e-9)


def test_sentiment_edge_cases():
    """Verify degeneracy handling for sentiment metrics."""
    # Zero total count returns None
    assert compute_sentiment_ratio(0, total_count=0) is None
    assert compute_sentiment_ratio(0, negative_count=0) is None

    # Missing internal or external SR yields None asymmetry
    assert compute_sentiment_asymmetry(None, 0.5) is None
    assert compute_sentiment_asymmetry(0.8, None) is None
    assert compute_sentiment_asymmetry(None, None) is None

    # Zero total weights yields None hostility isolation
    assert compute_hostility_weighted_isolation(0, 0, 0, 0) is None


def test_compute_community_sentiment_graph():
    """Verify complete community sentiment extraction from a NetworkX directed graph."""
    g = nx.DiGraph()
    # Community nodes: c1, c2
    # External node: ext
    # c1 -> c2: 8 positive, 2 negative (internal total = 10)
    # c1 -> ext: 3 positive, 7 negative (external total = 10)
    g.add_edge("c1", "c2", weight=10, positive_count=8, negative_count=2)
    g.add_edge("c1", "ext", weight=10, positive_count=3, negative_count=7)

    comm = {"c1", "c2"}
    result = compute_community_sentiment(g, comm)

    assert result["positive_internal_count"] == 8
    assert result["negative_internal_count"] == 2
    assert result["positive_external_count"] == 3
    assert result["negative_external_count"] == 7
    assert math.isclose(result["sr_internal"], 0.8, rel_tol=1e-9)
    assert math.isclose(result["sr_external"], 0.3, rel_tol=1e-9)
    assert math.isclose(result["sentiment_asymmetry"], 0.5, rel_tol=1e-9)

    # HI: weighted_internal = 8 + 0.5*2 = 9.0; weighted_external = 0.5*3 + 7 = 8.5
    # HI = 9.0 / (9.0 + 8.5) = 9.0 / 17.5 = 18 / 35
    assert math.isclose(result["hostility_weighted_isolation"], 9.0 / 17.5, rel_tol=1e-9)
