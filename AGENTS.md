# Agent Guidelines & Developer Notes

This document provides architectural guidance and developer notes for AI coding agents and human contributors interacting with the `echochamber` repository.

## 1. Core Design Patterns
- **Path Resolution**: Always use `pathlib.Path` via `echochamber.paths.resolve_path`. Avoid raw Unix string concats (`/`) on Windows.
- **Deterministic Sorts**: NetworkX node iteration order is preserved from graph construction. Always sort node names prior to calling `g.add_node()`.
- **Memory Conservation**: Never compute pairwise $m \times m$ cosine matrices in Python for community homogeneity. Use `compute_homogeneity_from_matrix` in `echochamber.metrics.homogeneity`, which leverages the $O(m \cdot d)$ vector-sum formula.
- **CSV Formula Injection**: All tabular outputs exported to CSV must go through `export_safe_csv` in `echochamber.storage.io`, which prefixes cell values starting with `=`, `+`, `-`, or `@` with a single quote (`'`).
- **Pydantic Validation**: All configuration dictionaries must validate against `EchoChamberConfig` in `echochamber.config`. ECI weights must sum to $1.0$ within $10^{-5}$ tolerance.

## 2. Directory Structure Conventions
- `data/fixture/`: Deterministic synthetic test fixtures (clearly marked with `# SYNTHETIC TEST DATA`).
- `data/raw/`: External Stanford SNAP downloads.
- `data/interim/`: Intermediate parquet caches and quarantine logs.
- `results/<run_name>/`: Self-contained execution bundles containing parquet metrics, markdown/csv summary tables, static plots, interactive HTML, and `manifest.json`.

## 3. Testing Standard
- Pytest must be run with `-v --tb=short`.
- Unit tests in `tests/test_metrics.py` assert exact numerical bounds for $I, H, D, S, \text{ECI}$.
- Integration test in `tests/test_pipeline.py` ensures all 10 pipeline stages run to completion without error.
