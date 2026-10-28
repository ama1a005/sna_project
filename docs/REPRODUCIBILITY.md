# Reproducibility Guide

This repository guarantees deterministic, bit-for-bit reproducible results across execution environments.

## 1. Quickstart Reproduction

To reproduce all results, tables, and figures from scratch:

```powershell
# 1. Activate environment
.\.venv\Scripts\Activate.ps1

# 2. Run the deterministic fixture pipeline
echochamber run --config configs/fixture.yaml

# 3. Execute the full unit and integration test suite
pytest -v

# 4. Launch the Streamlit dashboard
streamlit run app/Home.py
```

## 2. Determinism Guarantees
- **Seeded Partitions**: Louvain algorithm uses deterministic seed `seed: 42`.
- **Deterministic Node Ordering**: All nodes are sorted alphabetically before directed graph instantiation to eliminate graph dictionary hash randomizations.
- **Ties in Partition ID**: Community ranking sorts by descending size `(-len(nodes))` and breaks ties by the alphabetical name of the first node `nodes[0]`.
- **Hungarian Tracking**: Cost matrix and pairwise Jaccard computations evaluate in deterministic sorted order of community identifiers.
- **Manifest Tracking**: Every execution writes `results/<run>/manifest.json` recording the SHA256 configuration hash, Python version, OS platform, and stage runtimes.
