"""Tests for temporal community tracking and persistent track ID assignment."""

import re
import pytest

from echochamber.graph.tracking import jaccard_similarity, track_communities_across_windows


def test_jaccard_similarity():
    """Verify Jaccard calculation and intersection."""
    s1 = {"a", "b", "c"}
    s2 = {"b", "c", "d"}
    sim, inter = jaccard_similarity(s1, s2)
    # inter = 2, union = 4 -> sim = 0.5
    assert sim == 0.5
    assert inter == 2


def test_track_communities_format_and_persistence():
    """Verify Hungarian matching and Track ID format: T{index:05d}."""
    window_communities = {
        "2014Q1": {
            "2014Q1-C0001": ["python", "datascience", "machinelearning"],
            "2014Q1-C0002": ["games", "pcgaming", "nintendo"],
        },
        "2014Q2": {
            # Same python group survives with slight variation
            "2014Q2-C0001": ["python", "datascience", "programming"],
            # Brand new community
            "2014Q2-C0002": ["music", "hiphopheads", "metal"],
        },
    }

    tracking_df, comm_to_track = track_communities_across_windows(
        window_communities,
        min_jaccard=0.2,
        min_intersection=2,
    )

    assert not tracking_df.empty
    # Validate Track ID format
    for tid in tracking_df["track_id"]:
        assert re.match(r"^T\d{5}$", tid) is not None

    # Track ID for python group in 2014Q1 and 2014Q2 should match
    track_q1 = comm_to_track[("2014Q1", "2014Q1-C0001")]
    track_q2 = comm_to_track[("2014Q2", "2014Q2-C0001")]
    assert track_q1 == track_q2

    # New music group should have a new track ID
    track_music = comm_to_track[("2014Q2", "2014Q2-C0002")]
    assert track_music != track_q1
