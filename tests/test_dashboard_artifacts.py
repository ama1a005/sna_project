"""Tests for artifact loader, CSV injection defense, and dashboard schemas."""

from pathlib import Path
import pandas as pd
import pytest

from echochamber.storage.io import export_safe_csv, sanitize_cell_for_csv
from app.artifact_loader import list_available_runs, load_run_dataframe, load_run_manifest


def test_csv_injection_sanitization():
    """Verify that dangerous formula triggers (=, +, -, @) are sanitized with single quote prefix."""
    assert sanitize_cell_for_csv("=1+1") == "'=1+1"
    assert sanitize_cell_for_csv("+SUM(A1:A10)") == "'+SUM(A1:A10)"
    assert sanitize_cell_for_csv("-100") == "'-100"
    assert sanitize_cell_for_csv("@username") == "'@username"
    assert sanitize_cell_for_csv("normal_text") == "normal_text"
    assert sanitize_cell_for_csv(123) == 123


def test_export_safe_csv(temp_dir: Path):
    """Verify that export_safe_csv writes sanitized values to file."""
    df = pd.DataFrame({
        "subreddit": ["=cmd|' /C calc'!A0", "+malicious", "normal_sub"],
        "metric": [0.5, 0.7, 0.9],
    })
    csv_path = temp_dir / "safe.csv"
    export_safe_csv(df, csv_path)

    # Read raw content to verify single quote prefix
    content = csv_path.read_text(encoding="utf-8")
    assert "'=cmd" in content
    assert "'+malicious" in content


def test_artifact_loader_fixture_run():
    """Verify listing and loading existing fixture run artifacts."""
    runs = list_available_runs()
    assert "fixture-default" in runs

    manifest = load_run_manifest("fixture-default")
    assert manifest.get("status") == "SUCCESS"

    metrics_df = load_run_dataframe("fixture-default", "metrics.parquet")
    assert not metrics_df.empty
    assert "eci" in metrics_df.columns
    assert "isolation" in metrics_df.columns
    assert "homogeneity" in metrics_df.columns
