"""Unit tests for core Echo Chamber metrics and exact numerical assertions."""

import math
import networkx as nx
import numpy as np
import pytest

from echochamber.metrics.diversity import compute_normalized_entropy
from echochamber.metrics.eci import compute_eci
from echochamber.metrics.homogeneity import (
    compute_homogeneity_from_matrix,
    compute_pairwise_cosine_brute_force,
)
from echochamber.metrics.isolation import compute_isolation


def test_isolation_exact_assertion():
    """Verify I(W_in=8, W_out=2) == 0.8."""
    g = nx.DiGraph()
    # Nodes in community: c1, c2
    # Internal: c1 -> c2 with weight 8
    # External: c1 -> ext with weight 2
    g.add_edge("c1", "c2", weight=8.0)
    g.add_edge("c1", "ext", weight=2.0)

    comm = {"c1", "c2"}
    iso, w_in, w_out = compute_isolation(g, comm)

    assert iso is not None
    assert math.isclose(iso, 0.8, rel_tol=1e-9)
    assert math.isclose(w_in, 8.0, rel_tol=1e-9)
    assert math.isclose(w_out, 2.0, rel_tol=1e-9)


def test_isolation_zero_outgoing():
    """Isolation should return None if no outgoing links exist."""
    g = nx.DiGraph()
    g.add_node("c1")
    iso, w_in, w_out = compute_isolation(g, {"c1"})
    assert iso is None
    assert w_in == 0.0
    assert w_out == 0.0


def test_homogeneity_identical_vectors():
    """Verify H(identical vectors) == 1.0."""
    v1 = np.array([1.0, 0.0, 0.0], dtype=np.float64)
    v2 = np.array([1.0, 0.0, 0.0], dtype=np.float64)
    mat = np.vstack([v1, v2])

    h, avg_cos, m, cov = compute_homogeneity_from_matrix(mat, total_node_count=2, minimum_coverage=0.5)
    assert h is not None
    assert avg_cos is not None
    assert math.isclose(avg_cos, 1.0, rel_tol=1e-9)
    assert math.isclose(h, 1.0, rel_tol=1e-9)


def test_homogeneity_opposite_vectors():
    """Verify H(opposite vectors) == 0.0."""
    v1 = np.array([1.0, 0.0, 0.0], dtype=np.float64)
    v2 = np.array([-1.0, 0.0, 0.0], dtype=np.float64)
    mat = np.vstack([v1, v2])

    h, avg_cos, m, cov = compute_homogeneity_from_matrix(mat, total_node_count=2, minimum_coverage=0.5)
    assert h is not None
    assert avg_cos is not None
    assert math.isclose(avg_cos, -1.0, rel_tol=1e-9)
    assert math.isclose(h, 0.0, abs_tol=1e-9)


def test_homogeneity_orthogonal_vectors():
    """Verify H(orthogonal vectors) == 0.5."""
    v1 = np.array([1.0, 0.0, 0.0], dtype=np.float64)
    v2 = np.array([0.0, 1.0, 0.0], dtype=np.float64)
    mat = np.vstack([v1, v2])

    h, avg_cos, m, cov = compute_homogeneity_from_matrix(mat, total_node_count=2, minimum_coverage=0.5)
    assert h is not None
    assert avg_cos is not None
    assert math.isclose(avg_cos, 0.0, abs_tol=1e-9)
    assert math.isclose(h, 0.5, rel_tol=1e-9)


def test_vector_sum_agrees_with_brute_force():
    """Verify that O(m*d) vector sum agrees with O(m^2 * d) brute force cosine."""
    rng = np.random.default_rng(42)
    m = 25
    d = 300
    # Generate random vectors and normalize to unit L2 norm
    raw = rng.normal(0, 1, size=(m, d))
    norms = np.linalg.norm(raw, axis=1, keepdims=True)
    unit_vecs = raw / norms

    brute_force_avg = compute_pairwise_cosine_brute_force(unit_vecs)
    h, vec_sum_avg, _, _ = compute_homogeneity_from_matrix(unit_vecs, total_node_count=m, minimum_coverage=0.5)

    assert vec_sum_avg is not None
    assert math.isclose(vec_sum_avg, brute_force_avg, rel_tol=1e-7, abs_tol=1e-7)


def test_external_diversity_balanced_2_of_4():
    """Verify D(balanced 2 of 4 destinations) == ln(2)/ln(4) == 0.5."""
    weights = [5.0, 5.0]  # equally split across 2 communities
    k_possible = 4

    d, s, entropy = compute_normalized_entropy(weights, k_possible=k_possible)

    expected_d = math.log(2.0) / math.log(4.0)
    assert math.isclose(expected_d, 0.5, rel_tol=1e-9)
    assert math.isclose(d, 0.5, rel_tol=1e-9)
    assert math.isclose(s, 0.5, rel_tol=1e-9)


def test_external_diversity_no_external_links():
    """Verify D(no external links) == 0.0 and S == 1.0."""
    d, s, entropy = compute_normalized_entropy([], k_possible=4)
    assert math.isclose(d, 0.0, abs_tol=1e-9)
    assert math.isclose(s, 1.0, rel_tol=1e-9)


def test_eci_exact_calculation():
    """Verify ECI(I=0.8, H=0.8, S=0.5) == 0.7 with equal weights."""
    eci, scorable = compute_eci(
        isolation=0.8,
        homogeneity=0.8,
        exposure_scarcity=0.5,
        w_isolation=1.0 / 3.0,
        w_homogeneity=1.0 / 3.0,
        w_scarcity=1.0 / 3.0,
    )

    assert scorable is True
    assert eci is not None
    assert math.isclose(eci, 0.7, rel_tol=1e-7)


def test_eci_unscorable_conditions():
    """ECI must be None if Isolation or Homogeneity is None."""
    eci1, scorable1 = compute_eci(isolation=None, homogeneity=0.8, exposure_scarcity=0.5)
    assert eci1 is None
    assert scorable1 is False

    eci2, scorable2 = compute_eci(isolation=0.8, homogeneity=None, exposure_scarcity=0.5)
    assert eci2 is None
    assert scorable2 is False
