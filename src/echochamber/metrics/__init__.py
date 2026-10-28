"""Metrics module: Isolation, Homogeneity, Diversity/Scarcity, ECI, and Coverage."""

from echochamber.metrics.coverage import compute_window_coverage_report
from echochamber.metrics.diversity import compute_community_external_diversity, compute_normalized_entropy
from echochamber.metrics.eci import compute_eci
from echochamber.metrics.homogeneity import (
    compute_community_homogeneity,
    compute_homogeneity_from_matrix,
    compute_pairwise_cosine_brute_force,
)
from echochamber.metrics.isolation import compute_isolation

__all__ = [
    "compute_community_external_diversity",
    "compute_community_homogeneity",
    "compute_eci",
    "compute_homogeneity_from_matrix",
    "compute_isolation",
    "compute_normalized_entropy",
    "compute_pairwise_cosine_brute_force",
    "compute_window_coverage_report",
]
