"""Page 4: Comparisons - Baselines, Null Models & Sensitivity Analysis."""

import streamlit as st

st.set_page_config(page_title="Comparisons - Echo Chamber", page_icon="🔬", layout="wide")

from app.artifact_loader import load_run_dataframe
from app.components import render_header, render_sidebar_run_selector

selected_run = render_sidebar_run_selector()
render_header("Ablations, Null Models & Sensitivity Analysis", "Rigorous statistical validation of echo chamber indicators")

if not selected_run:
    st.warning("Please run the pipeline first.")
    st.stop()

tab_baselines, tab_null, tab_sensitivity, tab_correlations = st.tabs([
    "📊 Baseline Variants (7 Models)",
    "🎲 Null Models",
    "🎛️ Sensitivity Sweeps",
    "🔗 Spearman Correlations",
])

with tab_baselines:
    st.markdown("### 7 ECI Ablation Baselines")
    st.markdown("""
    - **ECI Equal**: Balanced weighting $(1/3, 1/3, 1/3)$
    - **ECI Topo Only**: Topology only $(0.5, 0.0, 0.5)$
    - **ECI Content Only**: Semantic homogeneity only $(0.0, 1.0, 0.0)$
    - **ECI Isolation Only**: Pure boundary closure $(1.0, 0.0, 0.0)$
    - **ECI Scarcity Only**: External exposure diversity scarcity $(0.0, 0.0, 1.0)$
    - **ECI Content Heavy**: Heavy semantic weighting $(0.15, 0.70, 0.15)$
    - **ECI Topo Heavy**: Heavy boundary weighting $(0.45, 0.10, 0.45)$
    """)
    baselines_df = load_run_dataframe(selected_run, "baselines.parquet")
    if not baselines_df.empty:
        st.dataframe(baselines_df[[
            "window_id", "community_id", "eci_equal", "eci_topo_only",
            "eci_content_only", "eci_isolation_only", "eci_scarcity_only",
            "eci_content_heavy", "eci_topo_heavy"
        ]], use_container_width=True)

with tab_null:
    st.markdown("### Embedding Permutation Null Model")
    st.markdown("""
    Evaluates whether internal semantic homogeneity $H(C)$ is significantly higher than
    expected if subreddit vectors were randomly shuffled across graph nodes (preserving network topology).
    """)
    null_df = load_run_dataframe(selected_run, "null_model_results.parquet")
    if not null_df.empty:
        st.dataframe(null_df, use_container_width=True)
    else:
        st.info("Null model results not available.")

with tab_sensitivity:
    st.markdown("### Parameter Sensitivity Sweeps")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Louvain Resolution Parameter Sweep**")
        res_df = load_run_dataframe(selected_run, "sensitivity_resolution.parquet")
        if not res_df.empty:
            st.dataframe(res_df, use_container_width=True)
    with col2:
        st.markdown("**ECI Weight Variant Sensitivity**")
        weights_df = load_run_dataframe(selected_run, "sensitivity_weights.parquet")
        if not weights_df.empty:
            st.dataframe(weights_df, use_container_width=True)

with tab_correlations:
    st.markdown("### Spearman Rank Correlations")
    corr_df = load_run_dataframe(selected_run, "correlations.parquet")
    if not corr_df.empty:
        st.dataframe(corr_df, use_container_width=True)
    else:
        st.info("Correlations not available.")
