"""Run manifest and metadata tracker."""

from datetime import datetime, timezone
import hashlib
import platform
import sys
from pathlib import Path
from typing import Any
import yaml

from echochamber.storage.io import atomic_write_json


class RunManifest:
    """Tracks run configuration, environment, timings, and output artifacts."""

    def __init__(self, run_dir: Path, config_dict: dict[str, Any]):
        self.run_dir = run_dir.resolve()
        self.config_dict = config_dict
        self.start_time = datetime.now(timezone.utc).isoformat()
        self.end_time: str | None = None
        self.stage_timings: dict[str, float] = {}
        self.artifacts: list[str] = []
        self.status = "INITIALIZED"
        self.error: str | None = None

        # Compute config hash
        raw_cfg_str = yaml.dump(config_dict, sort_keys=True)
        self.config_hash = hashlib.sha256(raw_cfg_str.encode("utf-8")).hexdigest()

    def record_stage(self, stage_name: str, duration_sec: float) -> None:
        self.stage_timings[stage_name] = duration_sec

    def record_artifact(self, artifact_path: Path) -> None:
        try:
            rel = str(artifact_path.resolve().relative_to(self.run_dir))
        except ValueError:
            rel = str(artifact_path.resolve())
        if rel not in self.artifacts:
            self.artifacts.append(rel)

    def complete(self, status: str = "COMPLETED", error: str | None = None) -> Path:
        self.status = status
        self.error = error
        self.end_time = datetime.now(timezone.utc).isoformat()

        manifest_data = {
            "status": self.status,
            "error": self.error,
            "config_hash": self.config_hash,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "environment": {
                "python_version": sys.version,
                "platform": platform.platform(),
                "system": platform.system(),
            },
            "stage_timings": self.stage_timings,
            "artifacts": self.artifacts,
            "config": self.config_dict,
        }

        manifest_file = self.run_dir / "manifest.json"
        return atomic_write_json(manifest_data, manifest_file)
