"""Pytest fixtures for unit and integration testing."""

import tempfile
from pathlib import Path
import numpy as np
import pytest

from echochamber.config import EchoChamberConfig
from echochamber.data.embeddings import EmbeddingStore
from echochamber.data.fixtures import generate_synthetic_data


@pytest.fixture
def temp_dir(tmp_path: Path) -> Path:
    """Provide a clean temporary directory for tests."""
    return tmp_path


@pytest.fixture
def synthetic_fixture_data(temp_dir: Path) -> tuple[Path, Path]:
    """Generate deterministic synthetic test data files in temp_dir."""
    tsv_path, emb_path = generate_synthetic_data(temp_dir, seed=42, num_quarters=2)
    return tsv_path, emb_path


@pytest.fixture
def sample_embedding_store() -> EmbeddingStore:
    """Provide an in-memory EmbeddingStore with orthogonal and known vectors."""
    v1 = np.array([1.0, 0.0, 0.0] + [0.0] * 297, dtype=np.float64)
    v2 = np.array([0.0, 1.0, 0.0] + [0.0] * 297, dtype=np.float64)
    v3 = np.array([-1.0, 0.0, 0.0] + [0.0] * 297, dtype=np.float64)
    v4 = np.array([1.0, 0.0, 0.0] + [0.0] * 297, dtype=np.float64)  # identical to v1

    return EmbeddingStore({
        "node_a": v1,
        "node_b": v2,
        "node_c": v3,
        "node_d": v4,
    })


@pytest.fixture
def sample_config(temp_dir: Path) -> EchoChamberConfig:
    """Create a test configuration pointing to temp_dir."""
    return EchoChamberConfig(
        project={"name": "test-run", "seed": 42, "mode": "fixture"},
        paths={
            "raw_dir": str(temp_dir / "raw"),
            "interim_dir": str(temp_dir / "interim"),
            "results_root": str(temp_dir / "results"),
            "run_name": "pytest-run",
        },
    )
