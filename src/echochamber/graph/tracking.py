"""Temporal community tracking across time windows using Hungarian matching."""

from typing import Dict, List, Set, Tuple
import numpy as np
import pandas as pd
from scipy.optimize import linear_sum_assignment

from echochamber.logging_utils import setup_logger

logger = setup_logger("echochamber.graph.tracking")


def jaccard_similarity(set_a: set[str], set_b: set[str]) -> tuple[float, int]:
    """Compute Jaccard similarity and intersection size between two node sets."""
    intersection = len(set_a.intersection(set_b))
    union = len(set_a.union(set_b))
    if union == 0:
        return 0.0, 0
    return float(intersection / union), intersection


def track_communities_across_windows(
    window_communities: dict[str, dict[str, list[str]]],
    min_jaccard: float = 0.2,
    min_intersection: int = 2,
    strategy: str = "hungarian_one_to_one",
) -> tuple[pd.DataFrame, dict[tuple[str, str], str]]:
    """Match communities across sequential windows and assign persistent track IDs.

    Track ID format: 'T{index:05d}', e.g. 'T00001'.

    Returns:
        (tracking_df, community_to_track_id)
        where community_to_track_id maps (window_id, community_id) -> track_id.
    """
    sorted_windows = sorted(window_communities.keys())
    records: list[dict] = []
    comm_to_track: dict[tuple[str, str], str] = {}
    track_counter = 0

    if not sorted_windows:
        return pd.DataFrame(columns=[
            "track_id", "window_id", "community_id", "prev_community_id", "jaccard_similarity", "shared_nodes_count"
        ]), comm_to_track

    # Initialize first window
    first_w = sorted_windows[0]
    for c_id, nodes in window_communities[first_w].items():
        track_counter += 1
        t_id = f"T{track_counter:05d}"
        comm_to_track[(first_w, c_id)] = t_id
        records.append({
            "track_id": t_id,
            "window_id": first_w,
            "community_id": c_id,
            "prev_community_id": None,
            "jaccard_similarity": 1.0,
            "shared_nodes_count": len(nodes),
        })

    # Match consecutive windows: w_prev -> w_curr
    for i in range(1, len(sorted_windows)):
        w_prev = sorted_windows[i - 1]
        w_curr = sorted_windows[i]

        prev_comms = window_communities[w_prev]
        curr_comms = window_communities[w_curr]

        prev_ids = list(prev_comms.keys())
        curr_ids = list(curr_comms.keys())

        if not prev_ids or not curr_ids:
            for c_id, nodes in curr_comms.items():
                track_counter += 1
                t_id = f"T{track_counter:05d}"
                comm_to_track[(w_curr, c_id)] = t_id
                records.append({
                    "track_id": t_id,
                    "window_id": w_curr,
                    "community_id": c_id,
                    "prev_community_id": None,
                    "jaccard_similarity": 0.0,
                    "shared_nodes_count": 0,
                })
            continue

        # Build cost matrix
        k, m = len(prev_ids), len(curr_ids)
        cost_matrix = np.full((k, m), fill_value=1e6, dtype=np.float64)
        jaccard_matrix = np.zeros((k, m), dtype=np.float64)
        intersection_matrix = np.zeros((k, m), dtype=np.int64)

        prev_sets = [set(prev_comms[cid]) for cid in prev_ids]
        curr_sets = [set(curr_comms[cid]) for cid in curr_ids]

        for p_idx in range(k):
            for c_idx in range(m):
                j_sim, inter = jaccard_similarity(prev_sets[p_idx], curr_sets[c_idx])
                jaccard_matrix[p_idx, c_idx] = j_sim
                intersection_matrix[p_idx, c_idx] = inter
                if j_sim >= min_jaccard and inter >= min_intersection:
                    cost_matrix[p_idx, c_idx] = 1.0 - j_sim

        # Run Hungarian algorithm
        row_ind, col_ind = linear_sum_assignment(cost_matrix)
        matched_curr_indices: set[int] = set()

        for r, c in zip(row_ind, col_ind):
            j_sim = jaccard_matrix[r, c]
            inter = intersection_matrix[r, c]
            if j_sim >= min_jaccard and inter >= min_intersection:
                p_cid = prev_ids[r]
                c_cid = curr_ids[c]
                t_id = comm_to_track[(w_prev, p_cid)]
                comm_to_track[(w_curr, c_cid)] = t_id
                matched_curr_indices.add(c)
                records.append({
                    "track_id": t_id,
                    "window_id": w_curr,
                    "community_id": c_cid,
                    "prev_community_id": p_cid,
                    "jaccard_similarity": j_sim,
                    "shared_nodes_count": inter,
                })

        # Unmatched communities in w_curr start new tracks
        for c_idx in range(m):
            if c_idx not in matched_curr_indices:
                c_cid = curr_ids[c_idx]
                track_counter += 1
                t_id = f"T{track_counter:05d}"
                comm_to_track[(w_curr, c_cid)] = t_id
                records.append({
                    "track_id": t_id,
                    "window_id": w_curr,
                    "community_id": c_cid,
                    "prev_community_id": None,
                    "jaccard_similarity": 0.0,
                    "shared_nodes_count": 0,
                })

    tracking_df = pd.DataFrame(records)
    logger.info(
        "Tracked communities across %d windows: assigned %d unique track IDs",
        len(sorted_windows),
        track_counter,
    )
    return tracking_df, comm_to_track
