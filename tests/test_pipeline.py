"""Integration tests for the 10-stage pipeline runner."""

from pathlib import Path
import pytest

from echochamber.config import EchoChamberConfig
from echochamber.pipeline.runner import run_pipeline


def test_full_pipeline_run_integration(temp_dir: Path):
    """Test full pipeline execution on a temporary directory with fixture data."""
    config = EchoChamberConfig(
        project={"name": "test-pipeline", "seed": 42, "mode": "fixture"},
        paths={
            "raw_dir": str(temp_dir / "raw"),
            "interim_dir": str(temp_dir / "interim"),
            "results_root": str(temp_dir / "results"),
            "run_name": "integration-test-run",
        },
        windows={
            "type": "calendar_quarter",
            "start": "2014-01-01T00:00:00Z",
            "end_exclusive": "2014-07-01T00:00:00Z",
            "include_empty": True,
            "min_event_count_for_analysis": 5,
        },
        analysis={
            "bootstrap_resamples": 20,
            "bootstrap_seed: 42": 42,
            "null_permutations": 10,
            "max_plot_nodes": 50,
        },
    )

    result = run_pipeline(config, base_dir=temp_dir)
    assert result["status"] == "SUCCESS"
    assert result["run_dir"].exists()
    assert (result["run_dir"] / "manifest.json").exists()
    assert (result["run_dir"] / "metrics.parquet").exists()
    assert (result["run_dir"] / "communities.parquet").exists()
    assert (result["run_dir"] / "tracking.parquet").exists()
    assert (result["run_dir"] / "baselines.parquet").exists()
    assert (result["run_dir"] / "plots" / "eci_distribution.png").exists()
