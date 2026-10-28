# Configuration Schema Documentation

This document describes the configuration structure used across `echochamber`.

## Sections

### `project`
- `name` (str): Identifier for the experiment run.
- `seed` (int): Random seed used for reproducible community detection, bootstrapping, and null models (default: `42`).
- `mode` (str): `"fixture"`, `"snap"`, or `"robustness"`.

### `paths`
- `raw_dir` (str): Directory containing raw input files (e.g. `data/raw` or `data/fixture`).
- `interim_dir` (str): Directory for intermediate parquet/cache files (default: `data/interim`).
- `results_root` (str): Directory where run output artifacts and plots are saved (default: `results`).
- `run_name` (str): Subdirectory name within `results_root` for this execution.

### `input`
- `hyperlink_files` (list[str]): List of TSV files containing hyperlinks between subreddits.
- `embedding_file` (str): CSV file containing 300D subreddit embeddings.
- `timezone` (str): Timezone for parsing timestamps (default: `"UTC"`).
- `duplicate_policy` (str): Policy for handling duplicate hyperlink posts (`"same-post-source-target"`).
- `invalid_row_policy` (str): `"quarantine"` or `"drop"`.
- `self_loop_policy` (str): `"drop-and-count"`.
- `missing_embedding_policy` (str): `"exclude-from-similarity"`.
- `name_policy` (str): `"strip-and-casefold"`.

### `windows`
- `type` (str): Windowing strategy (`"calendar_quarter"`).
- `start` (str, ISO8601): Window generation start time (e.g. `"2014-01-01T00:00:00Z"`).
- `end_exclusive` (str, ISO8601): Window generation end time (e.g. `"2015-01-01T00:00:00Z"`).
- `include_empty` (bool): Whether to record windows with zero events.
- `min_event_count_for_analysis` (int): Minimum edge events required in a window to proceed with community detection.

### `network`
- `edge_weight` (str): `"event_count"`.
- `negative_label_handling` (str): `"ignore_sign_for_topology"`.
- `detector_projection` (str): `"undirected_sum"`.
- `include_isolated_nodes_from_global_universe` (bool): Whether to add nodes from outside the window (default: `false`).

### `community_detection`
- `algorithm` (str): `"louvain"`.
- `resolution` (float): Louvain resolution parameter (default: `1.0`).
- `seed` (int): Community detection seed (default: `42`).
- `minimum_report_size` (int): Minimum members for a community to be analyzed (default: `2` or `3`).
- `minimum_report_edge_events` (int): Minimum internal/external edge events.

### `metrics`
- `isolation.mode`: `"outgoing_volume"`: $I = W_{in} / (W_{in} + W_{out})$. Null if $W_{in} + W_{out} == 0$.
- `homogeneity.mapping`: `"cosine_to_unit_interval"`: $H = (\text{avg\_cos} + 1) / 2$.
- `homogeneity.minimum_coverage`: Fraction of community members with valid embeddings (e.g. `0.5` or `0.7`).
- `homogeneity.minimum_embedded_nodes`: Minimum embedded nodes required (e.g. `2`).
- `external_diversity.entropy_denominator`: `"reachable_external_communities"` or `"all_external_communities"`.
- `external_diversity.zero_external_policy`: `"no_exposure_as_zero_diversity"`.

### `eci`
- `weights.isolation` (float): Weight $w_I$.
- `weights.homogeneity` (float): Weight $w_H$.
- `weights.exposure_scarcity` (float): Weight $w_S$.
- Note: $w_I + w_H + w_S$ must sum to $1.0$ within tolerance $10^{-5}$.

### `tracking`
- `min_jaccard` (float): Minimum Jaccard overlap to consider matching communities across windows (default: `0.2`).
- `min_intersection` (int): Minimum shared nodes (default: `2`).
- `strategy` (str): `"hungarian_one_to_one"`.

### `analysis`
- `bootstrap_resamples` (int): Number of bootstrap iterations for confidence intervals.
- `bootstrap_seed` (int): Seed for bootstrap sampling.
- `null_permutations` (int): Number of embedding permutations for null model testing.
- `max_plot_nodes` (int): Maximum nodes in bounded network visualizations.
