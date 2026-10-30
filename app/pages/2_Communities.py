"""Page 2: Communities - Echo Chamber Leaderboard & Network Subgraphs."""

import streamlit as st

st.set_page_config(page_title="Communities - Echo Chamber", page_icon="👥", layout="wide")

from app.artifact_loader import get_plot_path, load_run_dataframe
from app.components import render_header, render_sidebar_run_selector

selected_run = render_sidebar_run_selector()
render_header("Community Explorer & Echo Chamber Leaderboard", "Detailed inspection of detected community clusters and their member subreddits")

if not selected_run:
    st.warning("Please run the pipeline first.")
    st.stop()

metrics_df = load_run_dataframe(selected_run, "metrics.parquet")
comm_nodes_df = load_run_dataframe(selected_run, "communities.parquet")

if metrics_df.empty:
    st.warning("Metrics data not available for this run.")
    st.stop()

# Filter by window
windows = sorted(metrics_df["window_id"].unique())
selected_window = st.selectbox("Select Time Window", ["All Windows", *windows], index=0)

filtered_df = metrics_df if selected_window == "All Windows" else metrics_df[metrics_df["window_id"] == selected_window]

st.markdown("### 🏆 Top Echo Chamber Communities")
top_k = st.slider("Number of communities to display", min_value=5, max_value=50, value=10)
sorted_df = filtered_df.sort_values(by="eci", ascending=False).head(top_k)

st.dataframe(
    sorted_df[[
        "window_id", "community_id", "track_id", "node_count",
        "isolation", "homogeneity", "exposure_scarcity", "eci", "scorable"
    ]],
    use_container_width=True,
)

# Detailed inspection
st.markdown("### 🔍 Community Subreddit Members")
comm_list = sorted_df["community_id"].tolist()
if comm_list:
    selected_comm = st.selectbox("Inspect Community Members", comm_list)
    if not comm_nodes_df.empty:
        members = comm_nodes_df[comm_nodes_df["community_id"] == selected_comm]["subreddit"].tolist()
        st.write(f"**Members of `{selected_comm}` ({len(members)} subreddits):**")
        st.write(", ".join([f"`r/{m}`" for m in sorted(members)]))

# Community subgraph
st.markdown("### 🕸️ Community Subview Graph")
subgraph_plot = get_plot_path(selected_run, "community_subgraph.png")
if subgraph_plot and subgraph_plot.exists():
    st.image(subgraph_plot.read_bytes(), caption="Induced Subgraph of Detected Communities")
else:
    st.info("Community subgraph visualization not generated for this run.")
