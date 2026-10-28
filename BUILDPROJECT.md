# Project Build Specification: Temporal Echo Chamber Detection in Online Social Networks

**Project Title:** 23CSE356 Social Network Analysis — Temporal Echo Chamber Detection in Online Social Networks  
**Target Repository Location:** `C:\Users\amala\.gemini\antigravity\scratch\temporal-echo-chambers`  
**Execution Environment:** Windows, Python 3.11+, NetworkX 3.1+, Streamlit 1.28+, PyArrow, PyYAML, Typer, Plotly, Scikit-learn, Scipy

---

## 1. Project Objectives & Deliverables
1. **CLI Execution**: Command-line entry point `echochamber` with commands `run`, `validate`, `fixture`, `download`, `dashboard`, `version`.
2. **Data Pipeline**: Ingestion and cleaning of Stanford SNAP Reddit Hyperlink TSVs and 300D Subreddit Embeddings CSV.
3. **Temporal Windowing**: Discretization into calendar quarters (e.g. `2014Q1`, `2014Q2`).
4. **Graph Construction**: Directed weighted graphs ($W(u, v) = \text{event count}$) and undirected projections.
5. **Community Detection & Diagnostics**: Seeded Louvain community detection with deterministic sorting and ID formatting (`{window_id}-C{index:04d}`).
6. **Longitudinal Tracking**: Hungarian matching on Jaccard node similarity across consecutive quarters (`T{index:05d}`).
7. **Echo Chamber Metrics**:
   - Isolation $I(C, t) = W_{\text{in}} / (W_{\text{in}} + W_{\text{out}})$
   - Homogeneity $H(C) = (\text{avg\_cos} + 1) / 2$ via $O(m \cdot d)$ vector-sum identity
   - Exposure Scarcity $S(C, t) = 1 - D(C, t)$
   - ECI $= w_I \cdot I + w_H \cdot H + w_S \cdot S$
8. **Statistical Validation**: 7 ablation baselines, embedding permutation null models, bootstrap confidence intervals, Spearman rank correlations.
9. **Interactive Dashboard**: Multi-page Streamlit application with cached artifact loading.
10. **Test Suite**: 33 unit and integration tests asserting exact numerical properties.

---

## 2. Directory Layout
```
temporal-echo-chambers/
├── BUILDPROJECT.md
├── README.md
├── AGENTS.md
├── LICENSE-or-ATTRIBUTION.md
├── pyproject.toml
├── .gitignore
├── echochamber.bat
├── configs/
│   ├── fixture.yaml
│   ├── snap.yaml
│   ├── robustness.yaml
│   └── schema.md
├── src/echochamber/
│   ├── __init__.py
│   ├── __main__.py
│   ├── cli.py
│   ├── config.py
│   ├── paths.py
│   ├── logging_utils.py
│   ├── exceptions.py
│   ├── data/
│   │   ├── __init__.py
│   │   ├── download.py
│   │   ├── schema.py
│   │   ├── ingest.py
│   │   ├── clean.py
│   │   ├── embeddings.py
│   │   ├── windows.py
│   │   └── fixtures.py
│   ├── graph/
│   │   ├── __init__.py
│   │   ├── build.py
│   │   ├── partitions.py
│   │   ├── diagnostics.py
│   │   └── tracking.py
│   ├── metrics/
│   │   ├── __init__.py
│   │   ├── isolation.py
│   │   ├── homogeneity.py
│   │   ├── diversity.py
│   │   ├── eci.py
│   │   └── coverage.py
│   ├── analysis/
│   │   ├── __init__.py
│   │   ├── baselines.py
│   │   ├── sensitivity.py
│   │   ├── null_models.py
│   │   ├── statistics.py
│   │   └── report_tables.py
│   ├── pipeline/
│   │   ├── __init__.py
│   │   ├── stages.py
│   │   ├── runner.py
│   │   └── manifest.py
│   ├── visualization/
│   │   ├── __init__.py
│   │   ├── plots.py
│   │   └── graph_subview.py
│   └── storage/
│       ├── __init__.py
│       ├── schemas.py
│       └── io.py
├── app/
│   ├── Home.py
│   ├── components.py
│   ├── artifact_loader.py
│   └── pages/
│       ├── 1_Overview.py
│       ├── 2_Communities.py
│       ├── 3_Temporal_Trends.py
│       ├── 4_Comparisons.py
│       └── 5_Methodology.py
├── tests/
│   ├── conftest.py
│   ├── test_ingest.py
│   ├── test_embeddings.py
│   ├── test_windows.py
│   ├── test_graph.py
│   ├── test_community.py
│   ├── test_metrics.py
│   ├── test_tracking.py
│   ├── test_pipeline.py
│   ├── test_statistical_checks.py
│   ├── test_dashboard_artifacts.py
│   └── fixtures/
├── scripts/
│   ├── run_fixture.ps1
│   └── run_real.ps1
├── docs/
│   ├── IMPLEMENTATION_STATUS.md
│   ├── METHODS.md
│   ├── RESULTS.md
│   ├── DATA_DICTIONARY.md
│   ├── EXPERIMENTS.md
│   ├── LIMITATIONS.md
│   ├── TROUBLESHOOTING.md
│   └── REPRODUCIBILITY.md
├── data/
│   ├── raw/.gitkeep
│   ├── interim/.gitkeep
│   ├── processed/.gitkeep
│   └── fixture/.gitkeep
└── results/.gitkeep
```

---

## 3. Verification & Execution Status
- Test Suite: `pytest -v` $\to$ **33 passed** in 17.66s.
- Pipeline Run: `echochamber run --config configs/fixture.yaml` $\to$ Completed successfully in 7.41s.
- Manifest and all artifact tables/plots successfully generated in `results/fixture-default/`.
