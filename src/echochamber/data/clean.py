"""Data cleaning, deduplication, self-loop dropping, and window assignment."""

from pathlib import Path
import pandas as pd

from echochamber.data.windows import assign_windows
from echochamber.logging_utils import setup_logger

logger = setup_logger("echochamber.clean")


def clean_hyperlinks(
    df: pd.DataFrame,
    start_str: str | None = None,
    end_exclusive_str: str | None = None,
    duplicate_policy: str = "same-post-source-target",
    self_loop_policy: str = "drop-and-count",
) -> tuple[pd.DataFrame, dict[str, int]]:
    """Clean hyperlinks DataFrame by applying deduplication, self-loop filtering, and window assignment.

    Returns:
        (cleaned_df, stats_dict)
    """
    initial_count = len(df)
    stats = {
        "initial_count": initial_count,
        "duplicates_removed": 0,
        "self_loops_dropped": 0,
        "out_of_bounds_dropped": 0,
        "invalid_timestamps_dropped": 0,
        "final_count": 0,
    }

    if df.empty:
        stats["final_count"] = 0
        return df.copy(), stats

    # Parse timestamps and assign window IDs
    processed_df = assign_windows(df, timestamp_col="timestamp", window_col="window_id")

    # Drop rows with invalid timestamps
    valid_ts_mask = processed_df["timestamp"].notna()
    invalid_ts_count = int((~valid_ts_mask).sum())
    stats["invalid_timestamps_dropped"] = invalid_ts_count
    processed_df = processed_df[valid_ts_mask]

    # Date range filtering if specified
    if start_str:
        start_ts = pd.to_datetime(start_str, utc=True)
        in_range_mask = processed_df["timestamp"] >= start_ts
        stats["out_of_bounds_dropped"] += int((~in_range_mask).sum())
        processed_df = processed_df[in_range_mask]

    if end_exclusive_str:
        end_ts = pd.to_datetime(end_exclusive_str, utc=True)
        in_range_mask = processed_df["timestamp"] < end_ts
        stats["out_of_bounds_dropped"] += int((~in_range_mask).sum())
        processed_df = processed_df[in_range_mask]

    # Self-loop filtering
    if self_loop_policy == "drop-and-count":
        is_self_loop = processed_df["source_subreddit"] == processed_df["target_subreddit"]
        self_loop_count = int(is_self_loop.sum())
        stats["self_loops_dropped"] = self_loop_count
        processed_df = processed_df[~is_self_loop]

    # Deduplication
    if duplicate_policy == "same-post-source-target":
        # If post_id is empty, deduplicate on source, target, timestamp
        subset = ["source_subreddit", "target_subreddit", "post_id"]
        before_dedup = len(processed_df)
        processed_df = processed_df.drop_duplicates(subset=subset, keep="first")
        stats["duplicates_removed"] = before_dedup - len(processed_df)

    stats["final_count"] = len(processed_df)
    logger.info(
        "Cleaned hyperlinks: initial=%d, dropped: dups=%d, self_loops=%d, time_oob=%d, invalid_ts=%d -> final=%d",
        stats["initial_count"],
        stats["duplicates_removed"],
        stats["self_loops_dropped"],
        stats["out_of_bounds_dropped"],
        stats["invalid_timestamps_dropped"],
        stats["final_count"],
    )
    return processed_df.reset_index(drop=True), stats
