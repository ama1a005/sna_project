"""Configuration validation and loading using Pydantic v2."""

from pathlib import Path
from typing import Any
import yaml
from pydantic import BaseModel, Field, model_validator

from echochamber.exceptions import ConfigurationError
from echochamber.paths import resolve_path


class ProjectConfig(BaseModel):
    name: str = "temporal-echo-chambers"
    seed: int = 42
    mode: str = "fixture"  # fixture, snap, robustness


class PathsConfig(BaseModel):
    raw_dir: str = "data/raw"
    interim_dir: str = "data/interim"
    results_root: str = "results"
    run_name: str = "default-run"


class InputConfig(BaseModel):
    hyperlink_files: list[str] = Field(default_factory=lambda: ["fixture_hyperlinks.tsv"])
    embedding_file: str = "fixture_embeddings.csv"
    timezone: str = "UTC"
    duplicate_policy: str = "same-post-source-target"
    invalid_row_policy: str = "quarantine"
    self_loop_policy: str = "drop-and-count"
    missing_embedding_policy: str = "exclude-from-similarity"
    name_policy: str = "strip-and-casefold"


class WindowsConfig(BaseModel):
    type: str = "calendar_quarter"
    start: str = "2014-01-01T00:00:00Z"
    end_exclusive: str = "2015-01-01T00:00:00Z"
    include_empty: bool = True
    min_event_count_for_analysis: int = 10


class NetworkConfig(BaseModel):
    edge_weight: str = "event_count"
    negative_label_handling: str = "ignore_sign_for_topology"
    detector_projection: str = "undirected_sum"
    include_isolated_nodes_from_global_universe: bool = False


class CommunityDetectionConfig(BaseModel):
    algorithm: str = "louvain"
    resolution: float = 1.0
    seed: int = 42
    minimum_report_size: int = 2
    minimum_report_edge_events: int = 3


class IsolationConfig(BaseModel):
    mode: str = "outgoing_volume"


class HomogeneityConfig(BaseModel):
    mapping: str = "cosine_to_unit_interval"
    minimum_coverage: float = 0.5
    minimum_embedded_nodes: int = 2


class ExternalDiversityConfig(BaseModel):
    entropy_denominator: str = "reachable_external_communities"
    zero_external_policy: str = "no_exposure_as_zero_diversity"


class MetricsConfig(BaseModel):
    isolation: IsolationConfig = Field(default_factory=IsolationConfig)
    homogeneity: HomogeneityConfig = Field(default_factory=HomogeneityConfig)
    external_diversity: ExternalDiversityConfig = Field(default_factory=ExternalDiversityConfig)


class EciWeightsConfig(BaseModel):
    isolation: float = 1.0 / 3.0
    homogeneity: float = 1.0 / 3.0
    exposure_scarcity: float = 1.0 / 3.0

    @model_validator(mode="after")
    def validate_sum(self) -> "EciWeightsConfig":
        total = self.isolation + self.homogeneity + self.exposure_scarcity
        if abs(total - 1.0) > 1e-5:
            raise ValueError(f"ECI weights must sum to 1.0, got {total:.6f} (iso={self.isolation}, hom={self.homogeneity}, scar={self.exposure_scarcity})")
        return self


class EciConfig(BaseModel):
    weights: EciWeightsConfig = Field(default_factory=EciWeightsConfig)


class TrackingConfig(BaseModel):
    min_jaccard: float = 0.2
    min_intersection: int = 2
    strategy: str = "hungarian_one_to_one"


class AnalysisConfig(BaseModel):
    bootstrap_resamples: int = 50
    bootstrap_seed: int = 142
    null_permutations: int = 20
    max_plot_nodes: int = 100


class SweepConfig(BaseModel):
    resolutions: list[float] = Field(default_factory=lambda: [0.8, 1.0, 1.2])
    jaccard_thresholds: list[float] = Field(default_factory=lambda: [0.15, 0.20, 0.30])
    weight_variants: dict[str, list[float]] = Field(default_factory=dict)


class EchoChamberConfig(BaseModel):
    project: ProjectConfig = Field(default_factory=ProjectConfig)
    paths: PathsConfig = Field(default_factory=PathsConfig)
    input: InputConfig = Field(default_factory=InputConfig)
    windows: WindowsConfig = Field(default_factory=WindowsConfig)
    network: NetworkConfig = Field(default_factory=NetworkConfig)
    community_detection: CommunityDetectionConfig = Field(default_factory=CommunityDetectionConfig)
    metrics: MetricsConfig = Field(default_factory=MetricsConfig)
    eci: EciConfig = Field(default_factory=EciConfig)
    tracking: TrackingConfig = Field(default_factory=TrackingConfig)
    analysis: AnalysisConfig = Field(default_factory=AnalysisConfig)
    sweep: SweepConfig | None = None

    def get_run_dir(self, base_dir: Path | None = None) -> Path:
        """Get the absolute path for this run's outputs."""
        root = resolve_path(self.paths.results_root, base_dir)
        return root / self.paths.run_name

    def get_raw_dir(self, base_dir: Path | None = None) -> Path:
        """Get the absolute path for raw data."""
        return resolve_path(self.paths.raw_dir, base_dir)

    def get_interim_dir(self, base_dir: Path | None = None) -> Path:
        """Get the absolute path for interim data."""
        return resolve_path(self.paths.interim_dir, base_dir)


def load_config(config_path: str | Path) -> EchoChamberConfig:
    """Load and validate configuration from a YAML file."""
    path = Path(config_path).resolve()
    if not path.exists():
        raise ConfigurationError(f"Config file not found: {path}")

    try:
        with open(path, "r", encoding="utf-8") as f:
            raw_dict = yaml.safe_load(f) or {}
    except Exception as e:
        raise ConfigurationError(f"Failed to parse YAML from {path}: {e}") from e

    try:
        return EchoChamberConfig(**raw_dict)
    except Exception as e:
        raise ConfigurationError(f"Configuration validation failed for {path}: {e}") from e
