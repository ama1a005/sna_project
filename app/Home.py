"""Streamlit Home Dashboard - Temporal Echo Chamber Detection."""

import streamlit as st

st.set_page_config(
    page_title="Temporal Echo Chamber Detection",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="expanded",
)

from app.artifact_loader import load_run_dataframe, load_run_manifest
from app.components import render_header, render_sidebar_run_selector

selected_run = render_sidebar_run_selector()
render_header("Temporal Echo Chamber Detection in Online Social Networks", "23CSE356 Social Network Analysis Research Project")

if not selected_run:
    st.warning("Please execute the pipeline first using `echochamber run --config configs/fixture.yaml`.")
    st.stop()

manifest = load_run_manifest(selected_run)
metrics_df = load_run_dataframe(selected_run, "metrics.parquet")

cfg = manifest.get("config", {})
mode = cfg.get("project", {}).get("mode", "fixture")

if mode == "fixture":
    st.info("ℹ️ **SYNTHETIC TEST DATA NOTICE**: Currently visualizing synthetic test fixture data generated for testing and reproducibility.")
else:
    st.success(f"🌐 Visualizing Stanford SNAP Reddit Hyperlink network run: `{selected_run}`")

# Metric cards
if not metrics_df.empty:
    scorable = metrics_df[metrics_df["scorable"] == True]
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric("Total Communities", len(metrics_df))
    with col2:
        st.metric("Scorable Ratio", f"{(len(scorable)/len(metrics_df)*100):.1f}%" if len(metrics_df) else "0%")
    with col3:
        st.metric("Mean ECI", f"{scorable['eci'].mean():.3f}" if not scorable.empty else "N/A")
    with col4:
        st.metric("Mean Isolation", f"{scorable['isolation'].mean():.3f}" if not scorable.empty else "N/A")
    with col5:
        st.metric("Mean Homogeneity", f"{scorable['homogeneity'].mean():.3f}" if not scorable.empty else "N/A")

st.markdown("### 📋 Executive Summary & Navigation")
st.markdown("""
This research dashboard provides multidimensional quantification of temporal echo chambers across Reddit communities:

1. **[Overview](1_Overview)**: High-level quarterly network metrics, density, modularity, and global ECI distributions.
2. **[Communities](2_Communities)**: Detailed community rankings, node lists, subgraphs, and isolation vs. homogeneity trade-offs.
3. **[Temporal Trends](3_Temporal_Trends)**: Longitudinal tracking of community trajectories using Hungarian matching.
4. **[Comparisons](4_Comparisons)**: Baseline ablations, null models (embedding permutations), and sensitivity sweeps.
5. **[Methodology](5_Methodology)**: Formal mathematical formulas ($I, H, D, S, ECI$) and architecture details.
""")

st.markdown("### ⚙️ Pipeline Run Manifest")
col_l, col_r = st.columns(2)
with col_l:
    st.json({
        "status": manifest.get("status"),
        "config_hash": manifest.get("config_hash"),
        "start_time": manifest.get("start_time"),
        "end_time": manifest.get("end_time"),
        "environment": manifest.get("environment"),
    })
with col_r:
    st.markdown("**Stage Timings (seconds):**")
    timings = manifest.get("stage_timings", {})
    if timings:
        st.bar_chart(timings)
    else:
        st.write("No timing data available.")
