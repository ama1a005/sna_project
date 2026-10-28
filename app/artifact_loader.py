"""Cached artifact loader for the Streamlit dashboard."""

from pathlib import Path
from typing import Any
import pandas as pd
import streamlit as st

from echochamber.paths import PROJECT_ROOT, resolve_path
from echochamber.storage.io import read_json, read_parquet_df


def list_available_runs(results_root: Path | str | None = None) -> list[str]:
    """List subdirectories in results_root that contain a manifest.json."""
    root = resolve_path(results_root or "results", PROJECT_ROOT)
    if not root.exists():
        return []
    runs = []
    for d in sorted(root.iterdir()):
        if d.is_dir() and (d / "manifest.json").exists():
            runs.append(d.name)
    return runs


@st.cache_data
def load_run_manifest(run_name: str, results_root: str = "results") -> dict[str, Any]:
    """Load and cache run manifest."""
    root = resolve_path(results_root, PROJECT_ROOT)
    manifest_file = root / run_name / "manifest.json"
    if not manifest_file.exists():
        return {}
    return read_json(manifest_file)


@st.cache_data
def load_run_dataframe(run_name: str, filename: str, results_root: str = "results") -> pd.DataFrame:
    """Load and cache a parquet or CSV file from a run directory."""
    root = resolve_path(results_root, PROJECT_ROOT)
    fpath = root / run_name / filename
    if not fpath.exists():
        return pd.DataFrame()

    if fpath.suffix == ".parquet":
        return read_parquet_df(fpath)
    elif fpath.suffix == ".csv":
        return pd.read_csv(fpath)
    return pd.DataFrame()


def get_plot_path(run_name: str, plot_name: str, results_root: str = "results") -> Path | None:
    """Get absolute path to a generated plot image."""
    root = resolve_path(results_root, PROJECT_ROOT)
    p = root / run_name / "plots" / plot_name
    return p if p.exists() else None
