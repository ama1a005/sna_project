"""Storage schemas and standard column names."""

HYPERLINK_COLUMNS = [
    "source_subreddit",
    "target_subreddit",
    "post_id",
    "timestamp",
    "post_label",
    "properties",
]

CLEANED_HYPERLINK_COLUMNS = [
    "source_subreddit",
    "target_subreddit",
    "post_id",
    "timestamp",
    "post_label",
    "window_id",
]

COMMUNITY_COLUMNS = [
    "window_id",
    "community_id",
    "node_count",
    "internal_edge_count",
    "internal_weight",
    "external_weight",
    "total_weight",
]

COMMUNITY_NODES_COLUMNS = [
    "window_id",
    "community_id",
    "subreddit",
]

METRICS_COLUMNS = [
    "window_id",
    "community_id",
    "track_id",
    "node_count",
    "embedded_count",
    "embedding_coverage",
    "isolation",
    "homogeneity",
    "external_diversity",
    "exposure_scarcity",
    "eci",
    "scorable",
]

TRACKING_COLUMNS = [
    "track_id",
    "window_id",
    "community_id",
    "prev_community_id",
    "jaccard_similarity",
    "shared_nodes_count",
]
