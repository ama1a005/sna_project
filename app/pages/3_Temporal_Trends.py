"""Page 3: Temporal Trends - Longitudinal Tracking & Community Longevity."""

import plotly.express as px
import streamlit as st

st.set_page_config(page_title="Temporal Trends - Echo Chamber", page_icon="⏳", layout="wide")

from app.artifact_loader import get_plot_path, load_run_dataframe
from app.components import render_header, render_sidebar_run_selector

selected_run = render_sidebar_run_selector()
render_header("Temporal Evolution & Longitudinal Community Tracking", "Tracking echo chamber trajectories and persistence across time windows")

if not selected_run:
    st.warning("Please run the pipeline first.")
    st.stop()

tracking_df = load_run_dataframe(selected_run, "tracking.parquet")
metrics_df = load_run_dataframe(selected_run, "metrics.parquet")

if tracking_df.empty or metrics_df.empty:
    st.warning("Tracking data not available for this run.")
    st.stop()

st.markdown("### 📈 Longitudinal ECI Trajectories")
traj_plot = get_plot_path(selected_run, "temporal_trajectories.png")
if traj_plot and traj_plot.exists():
    st.image(str(traj_plot), use_container_width=True)

# Merge tracking with metrics
merged = pd_merged = pd_track = metrics_df.merge(tracking_df, on=["window_id", "community_id", "track_id"], how="inner")

if not merged.empty:
    fig = px.line(
        merged,
        x="window_id",
        y="eci",
        color="track_id",
        markers=True,
        title="Interactive ECI Trajectories by Track ID",
        labels={"window_id": "Quarter", "eci": "Echo Chamber Index (ECI)"},
    )
    st.plotly_chart(fig, use_container_width=True)

st.markdown("### 🧬 Hungarian Matching Transitions")
st.dataframe(
    tracking_df[[
        "track_id", "window_id", "community_id", "prev_community_id",
        "jaccard_similarity", "shared_nodes_count"
    ]],
    use_container_width=True,
)
