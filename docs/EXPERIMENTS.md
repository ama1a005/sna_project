# Experiment Catalog & Protocol

## 1. Primary Research Experiments

### Experiment 1: Baseline Index Comparison (Ablations)
- **Objective**: Determine whether all three factors (Isolation, Homogeneity, Exposure Scarcity) are required to capture polarization dynamics.
- **Protocol**: Compare the full model `eci_equal` against 6 variants (`eci_topo_only`, `eci_content_only`, `eci_isolation_only`, `eci_scarcity_only`, `eci_content_heavy`, `eci_topo_heavy`).
- **Configuration**: `configs/fixture.yaml` or `configs/snap.yaml`.
- **Outputs**: `results/<run>/baselines.parquet`.

### Experiment 2: Longitudinal Stability & Hungarian Tracking
- **Objective**: Track community persistence and identify whether echo chambers intensify or dissolve over sequential quarters.
- **Protocol**: Apply Hungarian matching between $t$ and $t+1$ with minimum Jaccard overlap $\ge 0.20$ and shared nodes $\ge 2$.
- **Outputs**: `results/<run>/tracking.parquet`, `results/<run>/plots/temporal_trajectories.png`.

### Experiment 3: Null Hypothesis Testing (Permutation Null)
- **Objective**: Statistically prove that community embedding homogeneity is not an artifact of random chance.
- **Protocol**: Shuffle 300D embedding vectors randomly across all active graph nodes $B=100$ times, leaving graph topology identical.
- **Outputs**: `results/<run>/null_model_results.parquet`.

### Experiment 4: Parameter Sensitivity Sweeps
- **Objective**: Test robustness to partitioning resolution and tracking thresholds.
- **Protocol**:
  - Resolution sweep: $\gamma \in \{0.8, 1.0, 1.2\}$.
  - Jaccard threshold: $J \in \{0.15, 0.20, 0.30\}$.
- **Configuration**: `configs/robustness.yaml`.
- **Outputs**: `results/<run>/sensitivity_resolution.parquet`, `results/<run>/sensitivity_weights.parquet`.
