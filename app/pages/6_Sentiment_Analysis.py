"""Page 6: Signed Sentiment Analysis - Polarity Stratification & Hostility Weighting."""

import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="Sentiment Analysis - Echo Chamber", page_icon="❤️", layout="wide")

from app.artifact_loader import load_run_dataframe
from app.components import render_header, render_sidebar_run_selector

selected_run = render_sidebar_run_selector()
render_header(
    "Signed Sentiment Isolation Analysis",
    "Decomposing hyperlink sentiment to distinguish true echo chambers from outward-hostile outrage machines",
)

if not selected_run:
    st.warning("Please select a pipeline run.")
    st.stop()

metrics_df = load_run_dataframe(selected_run, "metrics.parquet")
comms_df = load_run_dataframe(selected_run, "communities.parquet")

if metrics_df.empty:
    st.warning("No metrics data found for this run.")
    st.stop()

required_cols = ["sr_internal", "sr_external", "sentiment_asymmetry", "hostility_weighted_isolation"]
if not all(col in metrics_df.columns for col in required_cols):
    st.info("The selected run does not contain signed sentiment metrics. Please run the pipeline with sentiment analysis enabled.")
    st.stop()

# Helper to enrich with subreddit names
comm_subreddits = {}
if not comms_df.empty and "subreddit" in comms_df.columns:
    comm_subreddits = (
        comms_df.groupby(["window_id", "community_id"])["subreddit"]
        .apply(lambda s: ", ".join(list(s)[:5]) + (f" (+{len(s)-5} more)" if len(s) > 5 else ""))
        .to_dict()
    )

df_with_subs = metrics_df.copy()
df_with_subs["top_subreddits"] = df_with_subs.apply(
    lambda r: comm_subreddits.get((r["window_id"], r["community_id"]), ""),
    axis=1,
)

# Filter for valid sentiment asymmetry
valid_sa = df_with_subs[df_with_subs["sentiment_asymmetry"].notna()].copy()

# Summary Metrics Bar
st.markdown("### 📊 Polarity Isolation Summary")
col1, col2, col3, col4 = st.columns(4)

total_sentiment_comms = len(valid_sa)
mean_sa = valid_sa["sentiment_asymmetry"].mean() if total_sentiment_comms > 0 else 0.0
pos_sa_count = (valid_sa["sentiment_asymmetry"] > 0).sum()
neg_sa_count = (valid_sa["sentiment_asymmetry"] < 0).sum()

with col1:
    st.metric("Analyzed Communities", f"{total_sentiment_comms:,}")
with col2:
    st.metric("Mean Sentiment Asymmetry", f"{mean_sa:+.4f}")
with col3:
    pct_pos = (pos_sa_count / total_sentiment_comms * 100) if total_sentiment_comms else 0
    st.metric("Echo Chambers (SA > 0)", f"{pos_sa_count:,}", f"{pct_pos:.1f}%")
with col4:
    pct_neg = (neg_sa_count / total_sentiment_comms * 100) if total_sentiment_comms else 0
    st.metric("Outward Friendly (SA < 0)", f"{neg_sa_count:,}", f"{pct_neg:.1f}%")

st.markdown("---")

# 1. Sentiment Asymmetry Distribution by Window
st.markdown("### 📦 Sentiment Asymmetry Distribution Across Windows")
st.markdown(
    "Sentiment Asymmetry $SA(C,t) = SR_{\\text{internal}} - SR_{\\text{external}}$. "
    "Values greater than 0 indicate communities that are cordial internally but hostile to outsiders."
)

fig_box = px.box(
    valid_sa,
    x="window_id",
    y="sentiment_asymmetry",
    points="outliers",
    color="window_id",
    title="Quarterly Sentiment Asymmetry Distributions",
    labels={
        "window_id": "Calendar Quarter",
        "sentiment_asymmetry": "Sentiment Asymmetry (SR_in - SR_out)",
    },
)
fig_box.add_hline(y=0.0, line_dash="dash", line_color="gray", annotation_text="Neutral Line (SA = 0)")
fig_box.update_layout(showlegend=False, xaxis_tickangle=-45)
st.plotly_chart(fig_box, use_container_width=True)

# 2. Scatter: ECI vs Sentiment Asymmetry
st.markdown("### 🔬 ECI vs. Sentiment Asymmetry")
st.markdown(
    "**Research Hypothesis:** *Do high-ECI echo chambers exhibit systematically higher external hostility?* "
    "Points in the upper-right quadrant represent classic echo chambers (high structural isolation and high sentiment asymmetry)."
)

scorable_sa = valid_sa[valid_sa["scorable"] == True].copy()
if not scorable_sa.empty:
    fig_scatter = px.scatter(
        scorable_sa,
        x="sentiment_asymmetry",
        y="eci",
        color="isolation",
        size="node_count",
        hover_name="community_id",
        hover_data={
            "window_id": True,
            "sr_internal": ":.3f",
            "sr_external": ":.3f",
            "hostility_weighted_isolation": ":.3f",
            "top_subreddits": True,
        },
        title="ECI vs. Sentiment Asymmetry (Colored by Boundary Isolation)",
        labels={
            "sentiment_asymmetry": "Sentiment Asymmetry (SR_in - SR_out)",
            "eci": "Echo Chamber Index (ECI)",
            "isolation": "Boundary Isolation",
            "node_count": "Community Size",
        },
        color_continuous_scale="Viridis",
    )
    fig_scatter.add_vline(x=0.0, line_dash="dash", line_color="gray")
    st.plotly_chart(fig_scatter, use_container_width=True)
else:
    st.info("No scorable communities with sentiment data available for scatter plot.")

# 3. Temporal Trend of Mean SA Across Windows
st.markdown("### ⏳ Temporal Trend of Sentiment Asymmetry")
temporal_sa = (
    valid_sa.groupby("window_id")["sentiment_asymmetry"]
    .agg(
        mean_sa="mean",
        median_sa="median",
        std_sa="std",
        count="count",
    )
    .reset_index()
)

fig_trend = px.line(
    temporal_sa,
    x="window_id",
    y="mean_sa",
    markers=True,
    title="Mean Sentiment Asymmetry Trajectory Across Quarters",
    labels={"window_id": "Calendar Quarter", "mean_sa": "Mean Sentiment Asymmetry"},
)
fig_trend.add_hline(y=0.0, line_dash="dash", line_color="gray")
fig_trend.update_layout(xaxis_tickangle=-45)
st.plotly_chart(fig_trend, use_container_width=True)

# 4. Top 10 Tables
st.markdown("### 🏆 Extremal Sentiment Communities")
tab_pos, tab_neg = st.tabs(["🔥 Top 10 Echo Chambers by SA (Positive Inside, Hostile Outside)", "❄️ Top 10 Inverted Communities (Hostile Inside, Positive Outside)"])

display_cols = [
    "window_id",
    "community_id",
    "node_count",
    "top_subreddits",
    "sr_internal",
    "sr_external",
    "sentiment_asymmetry",
    "hostility_weighted_isolation",
    "eci",
]
fmt_dict = {
    "sr_internal": "{:.4f}",
    "sr_external": "{:.4f}",
    "sentiment_asymmetry": "{:+.4f}",
    "hostility_weighted_isolation": "{:.4f}",
    "eci": "{:.4f}",
}

with tab_pos:
    st.markdown("Communities with the highest positive asymmetry: internal interactions are overwhelmingly friendly/neutral while outgoing cross-community interactions are hostile.")
    top_pos_sa = (
        valid_sa.sort_values(by="sentiment_asymmetry", ascending=False)
        .head(10)[display_cols]
        .reset_index(drop=True)
    )
    st.dataframe(top_pos_sa.style.format(fmt_dict, na_rep="N/A"), use_container_width=True)

with tab_neg:
    st.markdown("Communities with the strongest negative asymmetry: highly critical/hostile internally, but positive toward external communities.")
    top_neg_sa = (
        valid_sa.sort_values(by="sentiment_asymmetry", ascending=True)
        .head(10)[display_cols]
        .reset_index(drop=True)
    )
    st.dataframe(top_neg_sa.style.format(fmt_dict, na_rep="N/A"), use_container_width=True)
