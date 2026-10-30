"""Page 1: Overview - Temporal Network & Community Distributions."""

from pathlib import Path
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="Overview - Echo Chamber", page_icon="📊", layout="wide")

from app.artifact_loader import get_plot_path, load_run_dataframe
from app.components import render_header, render_sidebar_run_selector

selected_run = render_sidebar_run_selector()
render_header("Network Overview & Global Distributions", "Quarterly community evolution and structural properties")

if not selected_run:
    st.warning("Please run the pipeline first.")
    st.stop()

metrics_df = load_run_dataframe(selected_run, "metrics.parquet")
window_summary_df = load_run_dataframe(selected_run, "summary_tables/window_summary.csv")

if window_summary_df.empty and not metrics_df.empty:
    st.write(metrics_df.head())
else:
    st.markdown("### 📅 Temporal Window Summary")
    st.dataframe(window_summary_df, use_container_width=True)

col_a, col_b = st.columns(2)

with col_a:
    st.markdown("### 📈 Echo Chamber Index (ECI) Distribution")
    dist_plot = get_plot_path(selected_run, "eci_distribution.png")
    if dist_plot and dist_plot.exists():
        st.image(dist_plot.read_bytes())
    elif not metrics_df.empty:
        scorable = metrics_df[metrics_df["scorable"] == True]
        fig = px.histogram(scorable, x="eci", nbins=15, title="ECI Distribution")
        st.plotly_chart(fig, use_container_width=True)

with col_b:
    st.markdown("### ⚖️ Isolation vs. Homogeneity Space")
    scatter_plot = get_plot_path(selected_run, "isolation_vs_homogeneity.png")
    if scatter_plot and scatter_plot.exists():
        st.image(scatter_plot.read_bytes())
    elif not metrics_df.empty:
        scorable = metrics_df[metrics_df["scorable"] == True]
        fig = px.scatter(
            scorable,
            x="isolation",
            y="homogeneity",
            color="eci",
            size="node_count",
            title="Isolation vs Homogeneity",
        )
        st.plotly_chart(fig, use_container_width=True)
