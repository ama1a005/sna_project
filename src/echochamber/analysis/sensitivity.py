"""Sensitivity and robustness analysis across hyperparameter variations."""

from typing import Any
import pandas as pd

from echochamber.analysis.baselines import BASELINE_VARIANTS
from echochamber.graph.partitions import detect_communities
from echochamber.logging_utils import setup_logger

logger = setup_logger("echochamber.analysis.sensitivity")


def run_resolution_sensitivity(
    graphs_by_window: dict[str, Any],
    resolutions: list[float] | None = None,
    seed: int = 42,
    minimum_report_size: int = 2,
) -> pd.DataFrame:
    """Analyze community detection sensitivity to Louvain resolution parameter."""
    res_list = resolutions or [0.8, 1.0, 1.2]
    records = []

    for res in res_list:
        for w_id, (di_g, undir_g) in graphs_by_window.items():
            comms, _ = detect_communities(
                undir_g,
                window_id=w_id,
                resolution=res,
                seed=seed,
                minimum_report_size=minimum_report_size,
            )
            sizes = [len(nodes) for nodes in comms.values()]
            records.append({
                "resolution": res,
                "window_id": w_id,
                "num_communities": len(comms),
                "mean_community_size": float(sum(sizes) / len(sizes)) if sizes else 0.0,
                "max_community_size": max(sizes) if sizes else 0,
            })

    return pd.DataFrame(records)


def run_weight_sensitivity(metrics_df: pd.DataFrame) -> pd.DataFrame:
    """Analyze ECI sensitivity across weight variants."""
    scorable_df = metrics_df[metrics_df["scorable"] == True]  # noqa: E712
    records = []

    for name, (w_i, w_h, w_s) in BASELINE_VARIANTS.items():
        if scorable_df.empty:
            continue

        scores = (
            w_i * scorable_df["isolation"] +
            w_h * scorable_df["homogeneity"] +
            w_s * scorable_df["exposure_scarcity"]
        )

        records.append({
            "variant": name,
            "weight_isolation": w_i,
            "weight_homogeneity": w_h,
            "weight_scarcity": w_s,
            "mean_eci": float(scores.mean()),
            "std_eci": float(scores.std()),
            "median_eci": float(scores.median()),
            "min_eci": float(scores.min()),
            "max_eci": float(scores.max()),
        })

    return pd.DataFrame(records)
