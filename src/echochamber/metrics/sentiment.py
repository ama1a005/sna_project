"""Signed sentiment-stratified isolation analysis.

Novel contribution: decompose hyperlink flow by sentiment to distinguish
echo chambers (high internal + positive) from outrage machines
(high internal + mostly hostile cross-community links).
"""

from typing import Any
import networkx as nx


def compute_sentiment_ratio(
    positive_count: int | float,
    total_count: int | float | None = None,
    negative_count: int | float | None = None,
) -> float | None:
    """Compute the fraction of links that are positive: SR = positive / total.

    Accepts either (positive_count, total_count) or (positive_count, negative_count=neg).
    Returns None if total links <= 0.
    """
    if total_count is None:
        if negative_count is None:
            raise ValueError("Either total_count or negative_count must be provided")
        total_count = positive_count + negative_count

    if total_count <= 0:
        return None

    return float(positive_count / total_count)


def compute_sentiment_asymmetry(
    sr_internal: float | None,
    sr_external: float | None,
) -> float | None:
    """Compute sentiment asymmetry SA(C, t) = SR_internal - SR_external.

    - SA > 0: positive internally, hostile externally -> classic echo chamber
    - SA < 0: hostile internally, positive externally -> unusual outward friendliness
    - SA ~ 0: sentiment-neutral community

    Returns None if either SR_internal or SR_external is None.
    """
    if sr_internal is None or sr_external is None:
        return None

    return float(sr_internal - sr_external)


def compute_hostility_weighted_isolation(
    pos_in: int | float,
    neg_in: int | float,
    pos_out: int | float,
    neg_out: int | float,
) -> float | None:
    """Compute hostility-weighted isolation HI(C, t).

    Weight internal links by 1.0 if positive, 0.5 if negative.
    Weight external links by 1.0 if negative, 0.5 if positive.

    Formula:
        weighted_internal = 1.0 * pos_in + 0.5 * neg_in
        weighted_external = 0.5 * pos_out + 1.0 * neg_out
        HI = weighted_internal / (weighted_internal + weighted_external)

    Amplifies the echo chamber score for communities that are friendly
    internally and hostile externally.
    Returns None if weighted_internal + weighted_external == 0.
    """
    weighted_internal = 1.0 * pos_in + 0.5 * neg_in
    weighted_external = 0.5 * pos_out + 1.0 * neg_out
    total_weighted = weighted_internal + weighted_external

    if total_weighted <= 0.0:
        return None

    return float(weighted_internal / total_weighted)


def compute_community_sentiment(
    di_graph: nx.DiGraph,
    community_nodes: set[str],
) -> dict[str, Any]:
    """Compute all sentiment isolation metrics for a community in a directed graph.

    Aggregates positive and negative edge counts for internal (within C) and
    external (outgoing to V \\ C) links, then computes:
        - sr_internal (float | None)
        - sr_external (float | None)
        - sentiment_asymmetry (float | None)
        - hostility_weighted_isolation (float | None)
        - positive_internal_count (int)
        - negative_internal_count (int)
        - positive_external_count (int)
        - negative_external_count (int)

    Returns:
        dict containing the 8 sentiment metric fields.
    """
    pos_in = 0
    neg_in = 0
    pos_out = 0
    neg_out = 0

    for u in community_nodes:
        if u not in di_graph:
            continue
        for _, v, data in di_graph.out_edges(u, data=True):
            pos = int(data.get("positive_count", 0))
            neg = int(data.get("negative_count", 0))

            # Backwards compatibility: if explicit counts absent, fall back to weight
            if pos == 0 and neg == 0 and "weight" in data:
                pos = int(data.get("weight", 1))

            if v in community_nodes:
                pos_in += pos
                neg_in += neg
            else:
                pos_out += pos
                neg_out += neg

    sr_in = compute_sentiment_ratio(pos_in, negative_count=neg_in)
    sr_out = compute_sentiment_ratio(pos_out, negative_count=neg_out)
    sa = compute_sentiment_asymmetry(sr_in, sr_out)
    hi = compute_hostility_weighted_isolation(pos_in, neg_in, pos_out, neg_out)

    return {
        "sr_internal": sr_in,
        "sr_external": sr_out,
        "sentiment_asymmetry": sa,
        "hostility_weighted_isolation": hi,
        "positive_internal_count": pos_in,
        "negative_internal_count": neg_in,
        "positive_external_count": pos_out,
        "negative_external_count": neg_out,
    }
