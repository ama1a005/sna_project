"""Pipeline orchestration and execution runner."""

import time
from pathlib import Path
from typing import Any

from echochamber.config import EchoChamberConfig
from echochamber.exceptions import PipelineExecutionError
from echochamber.logging_utils import setup_logger
from echochamber.pipeline.manifest import RunManifest
from echochamber.pipeline.stages import (
    stage_00_init,
    stage_01_ingest,
    stage_02_clean_window,
    stage_03_graph_build,
    stage_04_community_detection,
    stage_05_tracking,
    stage_06_metrics,
    stage_07_baselines_null,
    stage_08_sensitivity,
    stage_09_reports_plots,
)

logger = setup_logger("echochamber.pipeline.runner")


def run_pipeline(config: EchoChamberConfig, base_dir: Path | None = None) -> dict[str, Any]:
    """Execute the complete 10-stage temporal echo chamber pipeline."""
    logger.info("==================================================")
    logger.info("Starting Pipeline Execution: %s", config.project.name)
    logger.info("Mode: %s | Run Name: %s", config.project.mode, config.paths.run_name)
    logger.info("==================================================")

    t_start = time.time()
    run_dir = config.get_run_dir(base_dir)
    manifest = RunManifest(run_dir, config.model_dump())

    stages = [
        ("00_init", stage_00_init),
        ("01_ingest", stage_01_ingest),
        ("02_clean_window", stage_02_clean_window),
        ("03_graph_build", stage_03_graph_build),
        ("04_community_detection", stage_04_community_detection),
        ("05_tracking", stage_05_tracking),
        ("06_metrics", stage_06_metrics),
        ("07_baselines_null", stage_07_baselines_null),
        ("08_sensitivity", stage_08_sensitivity),
        ("09_reports_plots", stage_09_reports_plots),
    ]

    state: dict[str, Any] = {}

    try:
        # Stage 00 takes config and base_dir
        state = stage_00_init(config, base_dir)
        manifest.record_stage("00_init", state.get("duration", 0.0))

        # Subsequent stages take (config, state)
        for stage_name, stage_fn in stages[1:]:
            t_stage_start = time.time()
            state = stage_fn(config, state)
            stage_duration = time.time() - t_stage_start
            manifest.record_stage(stage_name, stage_duration)

        # Record generated artifacts from run_dir
        for p in run_dir.rglob("*"):
            if p.is_file() and p.name != "manifest.json":
                manifest.record_artifact(p)

        manifest_file = manifest.complete(status="SUCCESS")
        total_time = time.time() - t_start
        logger.info("Pipeline completed successfully in %.2f seconds! Manifest saved to %s", total_time, manifest_file)

        return {
            "status": "SUCCESS",
            "run_dir": run_dir,
            "manifest_file": manifest_file,
            "total_time": total_time,
            "metrics_df": state.get("metrics_df"),
        }

    except Exception as e:
        logger.exception("Pipeline failed with error: %s", e)
        manifest.complete(status="FAILED", error=str(e))
        raise PipelineExecutionError(f"Pipeline execution aborted at stage: {e}") from e
