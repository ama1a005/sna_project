"""Summary table generation for reports and safe CSV/Markdown exports."""

from pathlib import Path
import pandas as pd

from echochamber.storage.io import export_safe_csv


def generate_window_summary_table(metrics_df: pd.DataFrame) -> pd.DataFrame:
    """Summarize community counts and average metrics per temporal window."""
    if metrics_df.empty:
        return pd.DataFrame()

    grouped = metrics_df.groupby("window_id")
    summary = []

    for w_id, group in grouped:
        scorable = group[group["scorable"] == True]  # noqa: E712
        summary.append({
            "window_id": w_id,
            "total_communities": len(group),
            "scorable_communities": len(scorable),
            "mean_isolation": float(scorable["isolation"].mean()) if not scorable.empty else None,
            "mean_homogeneity": float(scorable["homogeneity"].mean()) if not scorable.empty else None,
            "mean_scarcity": float(scorable["exposure_scarcity"].mean()) if not scorable.empty else None,
            "mean_eci": float(scorable["eci"].mean()) if not scorable.empty else None,
            "median_eci": float(scorable["eci"].median()) if not scorable.empty else None,
        })

    return pd.DataFrame(summary)


def generate_top_echo_chambers_table(metrics_df: pd.DataFrame, top_k: int = 10) -> pd.DataFrame:
    """Extract top-K highest ECI communities across all windows."""
    scorable = metrics_df[metrics_df["scorable"] == True]  # noqa: E712
    if scorable.empty:
        return pd.DataFrame()

    sorted_df = scorable.sort_values(by="eci", ascending=False).head(top_k)
    cols = [
        "window_id",
        "community_id",
        "track_id",
        "node_count",
        "isolation",
        "homogeneity",
        "exposure_scarcity",
        "eci",
    ]
    avail_cols = [c for c in cols if c in sorted_df.columns]
    return sorted_df[avail_cols].reset_index(drop=True)


def export_markdown_table(df: pd.DataFrame, file_path: Path | str, title: str = "") -> Path:
    """Export a DataFrame to a GitHub Flavored Markdown table."""
    dest = Path(file_path).resolve()
    dest.parent.mkdir(parents=True, exist_ok=True)

    md_content = []
    if title:
        md_content.append(f"### {title}\n")
    md_content.append(df.to_markdown(index=False))
    md_content.append("\n")

    dest.write_text("\n".join(md_content), encoding="utf-8")
    return dest
