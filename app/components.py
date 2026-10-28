"""Reusable UI components for Streamlit dashboard."""

import streamlit as st
from app.artifact_loader import list_available_runs, load_run_manifest


def render_sidebar_run_selector() -> str | None:
    """Render run selector in the sidebar and return the chosen run_name."""
    st.sidebar.title("Configuration")
    runs = list_available_runs()

    if not runs:
        st.sidebar.warning("No completed pipeline runs found in results/.")
        st.sidebar.info("Run `echochamber run` first.")
        return None

    selected_run = st.sidebar.selectbox("Select Experiment Run", runs, index=0)
    manifest = load_run_manifest(selected_run)

    st.sidebar.markdown("---")
    st.sidebar.markdown(f"**Run:** `{selected_run}`")
    status = manifest.get("status", "UNKNOWN")
    if status == "SUCCESS":
        st.sidebar.success(f"Status: {status}")
    else:
        st.sidebar.error(f"Status: {status}")

    cfg = manifest.get("config", {})
    mode = cfg.get("project", {}).get("mode", "unknown")
    st.sidebar.caption(f"Mode: **{mode}** | Started: {manifest.get('start_time', 'N/A')[:19]}")

    return selected_run


def render_header(title: str, subtitle: str = "") -> None:
    """Render consistent page header."""
    st.title(title)
    if subtitle:
        st.markdown(f"*{subtitle}*")
    st.markdown("---")
