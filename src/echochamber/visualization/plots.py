"""Static and interactive plotting utilities for echo chamber metrics."""

from pathlib import Path
import matplotlib
matplotlib.use("Agg")  # Headless backend
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from echochamber.logging_utils import setup_logger

logger = setup_logger("echochamber.visualization.plots")


def plot_eci_distribution(
    metrics_df: pd.DataFrame,
    output_path: Path | str | None = None,
) -> plt.Figure:
    """Plot histogram and KDE of Echo Chamber Index (ECI) scores."""
    scorable = metrics_df[metrics_df["scorable"] == True]  # noqa: E712
    scores = scorable["eci"].dropna()

    fig, ax = plt.subplots(figsize=(8, 5))
    if not scores.empty:
        ax.hist(scores, bins=15, color="#2b5c8f", edgecolor="white", alpha=0.8, density=True)
        ax.axvline(scores.mean(), color="#d95f02", linestyle="--", linewidth=2, label=f"Mean: {scores.mean():.3f}")
        ax.axvline(scores.median(), color="#7570b3", linestyle=":", linewidth=2, label=f"Median: {scores.median():.3f}")
    ax.set_title("Distribution of Echo Chamber Index (ECI)", fontsize=13, fontweight="bold")
    ax.set_xlabel("Echo Chamber Index (ECI)", fontsize=11)
    ax.set_ylabel("Density", fontsize=11)
    ax.set_xlim(0, 1)
    ax.grid(True, linestyle="--", alpha=0.5)
    ax.legend(frameon=True)
    plt.tight_layout()

    if output_path:
        dest = Path(output_path).resolve()
        dest.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(dest, dpi=300)
        plt.close(fig)

    return fig


def plot_isolation_vs_homogeneity(
    metrics_df: pd.DataFrame,
    output_path: Path | str | None = None,
) -> plt.Figure:
    """Scatter plot of Isolation vs Embedding Homogeneity colored by ECI."""
    scorable = metrics_df[metrics_df["scorable"] == True].dropna(subset=["isolation", "homogeneity", "eci"])

    fig, ax = plt.subplots(figsize=(8, 6))
    if not scorable.empty:
        sizes = np.clip(scorable["node_count"] * 10, 30, 300)
        scatter = ax.scatter(
            scorable["isolation"],
            scorable["homogeneity"],
            c=scorable["eci"],
            cmap="viridis",
            s=sizes,
            alpha=0.8,
            edgecolors="k",
            linewidths=0.5,
        )
        cbar = plt.colorbar(scatter, ax=ax)
        cbar.set_label("ECI Score", fontsize=11)

    ax.set_title("Isolation vs. Embedding Homogeneity", fontsize=13, fontweight="bold")
    ax.set_xlabel("Boundary Isolation I(C)", fontsize=11)
    ax.set_ylabel("Embedding Homogeneity H(C)", fontsize=11)
    ax.set_xlim(-0.05, 1.05)
    ax.set_ylim(-0.05, 1.05)
    ax.grid(True, linestyle="--", alpha=0.5)
    plt.tight_layout()

    if output_path:
        dest = Path(output_path).resolve()
        dest.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(dest, dpi=300)
        plt.close(fig)

    return fig


def plot_temporal_trajectories(
    metrics_df: pd.DataFrame,
    output_path: Path | str | None = None,
    top_tracks: int = 5,
) -> plt.Figure:
    """Plot ECI over time for top persistent community tracks."""
    scorable = metrics_df[metrics_df["scorable"] == True]

    # Find tracks with highest observation count
    track_counts = scorable["track_id"].value_counts()
    frequent_tracks = track_counts.head(top_tracks).index.tolist()

    fig, ax = plt.subplots(figsize=(9, 5))
    for tid in frequent_tracks:
        track_data = scorable[scorable["track_id"] == tid].sort_values("window_id")
        ax.plot(
            track_data["window_id"],
            track_data["eci"],
            marker="o",
            linewidth=2,
            label=f"Track {tid}",
        )

    ax.set_title("Temporal Trajectory of Echo Chamber Index", fontsize=13, fontweight="bold")
    ax.set_xlabel("Time Window (Quarter)", fontsize=11)
    ax.set_ylabel("Echo Chamber Index (ECI)", fontsize=11)
    ax.set_ylim(0, 1.05)
    ax.grid(True, linestyle="--", alpha=0.5)
    ax.legend(frameon=True, bbox_to_anchor=(1.02, 1), loc="upper left")
    plt.tight_layout()

    if output_path:
        dest = Path(output_path).resolve()
        dest.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(dest, dpi=300)
        plt.close(fig)

    return fig


def create_interactive_scatter_html(
    metrics_df: pd.DataFrame,
    output_path: Path | str,
) -> Path:
    """Create an interactive Plotly HTML scatter visualization."""
    dest = Path(output_path).resolve()
    dest.parent.mkdir(parents=True, exist_ok=True)

    scorable = metrics_df[metrics_df["scorable"] == True].dropna(subset=["isolation", "homogeneity", "eci"])
    fig = px.scatter(
        scorable,
        x="isolation",
        y="homogeneity",
        color="eci",
        size="node_count",
        hover_data=["window_id", "community_id", "track_id", "exposure_scarcity"],
        title="Interactive Isolation vs Homogeneity Map",
        color_continuous_scale="Viridis",
        labels={"isolation": "Isolation I(C)", "homogeneity": "Homogeneity H(C)", "eci": "ECI"},
    )
    fig.write_html(str(dest))
    return dest
