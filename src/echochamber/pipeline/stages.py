"""Pipeline stages (00-09) for temporal echo chamber detection."""

import time
from pathlib import Path
from typing import Any
import pandas as pd

from echochamber.analysis.baselines import compute_baseline_variants
from echochamber.analysis.null_models import run_embedding_permutation_null
from echochamber.analysis.report_tables import (
    export_markdown_table,
    generate_top_echo_chambers_table,
    generate_window_summary_table,
)
from echochamber.analysis.sensitivity import run_resolution_sensitivity, run_weight_sensitivity
from echochamber.analysis.statistics import compute_bootstrap_ci, compute_spearman_correlations
from echochamber.config import EchoChamberConfig
from echochamber.data.clean import clean_hyperlinks
from echochamber.data.embeddings import EmbeddingStore, parse_embeddings_file
from echochamber.data.fixtures import generate_synthetic_data
from echochamber.data.ingest import ingest_hyperlinks_tsv
from echochamber.graph.build import build_directed_graph, project_undirected
from echochamber.graph.diagnostics import compute_network_diagnostics
from echochamber.graph.partitions import detect_communities
from echochamber.graph.tracking import track_communities_across_windows
from echochamber.logging_utils import setup_logger
from echochamber.metrics.diversity import compute_community_external_diversity
from echochamber.metrics.eci import compute_eci
from echochamber.metrics.homogeneity import compute_community_homogeneity
from echochamber.metrics.isolation import compute_isolation
from echochamber.storage.io import export_safe_csv, write_parquet_df
from echochamber.visualization.graph_subview import plot_community_subgraph
from echochamber.visualization.plots import (
    create_interactive_scatter_html,
    plot_eci_distribution,
    plot_isolation_vs_homogeneity,
    plot_temporal_trajectories,
)

logger = setup_logger("echochamber.pipeline.stages")


def stage_00_init(config: EchoChamberConfig, base_dir: Path | None = None) -> dict[str, Any]:
    """Stage 00: Initialize run environment, ensure paths, load embeddings."""
    t0 = time.time()
    logger.info("--- Stage 00: Initialization & Setup ---")
    run_dir = config.get_run_dir(base_dir)
    run_dir.mkdir(parents=True, exist_ok=True)
    raw_dir = config.get_raw_dir(base_dir)
    raw_dir.mkdir(parents=True, exist_ok=True)
    interim_dir = config.get_interim_dir(base_dir)
    interim_dir.mkdir(parents=True, exist_ok=True)

    emb_file = raw_dir / config.input.embedding_file

    # Auto-generate fixture data if in fixture mode and files missing
    if config.project.mode == "fixture" and (not emb_file.exists()):
        logger.info("Fixture mode selected: generating deterministic synthetic test data at %s", raw_dir)
        generate_synthetic_data(raw_dir, seed=config.project.seed)

    # Load embeddings into memory
    if emb_file.exists():
        embedding_store = parse_embeddings_file(emb_file)
    else:
        logger.warning("Embeddings file %s not found. Proceeding with empty embedding store.", emb_file)
        embedding_store = EmbeddingStore({})

    duration = time.time() - t0
    return {
        "run_dir": run_dir,
        "raw_dir": raw_dir,
        "interim_dir": interim_dir,
        "embedding_store": embedding_store,
        "duration": duration,
    }


def stage_01_ingest(config: EchoChamberConfig, state: dict[str, Any]) -> dict[str, Any]:
    """Stage 01: Ingestion & Quarantine."""
    t0 = time.time()
    logger.info("--- Stage 01: Ingestion & Quarantine ---")
    raw_dir: Path = state["raw_dir"]
    interim_dir: Path = state["interim_dir"]
    dfs = []

    for fname in config.input.hyperlink_files:
        fpath = raw_dir / fname
        if not fpath.exists():
            if config.project.mode == "fixture":
                logger.info("Generating fixture data for missing file %s", fpath)
                generate_synthetic_data(raw_dir, seed=config.project.seed)
            else:
                logger.warning("Input file %s does not exist", fpath)
                continue

        quarantine_file = interim_dir / f"quarantine_{fname}.parquet"
        df = ingest_hyperlinks_tsv(
            fpath,
            quarantine_path=quarantine_file,
            name_policy=config.input.name_policy,
        )
        dfs.append(df)

    combined_raw_df = pd.concat(dfs, ignore_index=True) if dfs else pd.DataFrame()
    logger.info("Ingested total of %d raw hyperlink records", len(combined_raw_df))
    duration = time.time() - t0
    state["raw_df"] = combined_raw_df
    state["duration_01"] = duration
    return state


def stage_02_clean_window(config: EchoChamberConfig, state: dict[str, Any]) -> dict[str, Any]:
    """Stage 02: Cleaning & Window Assignment."""
    t0 = time.time()
    logger.info("--- Stage 02: Cleaning & Windowing ---")
    raw_df: pd.DataFrame = state["raw_df"]

    cleaned_df, stats = clean_hyperlinks(
        raw_df,
        start_str=config.windows.start,
        end_exclusive_str=config.windows.end_exclusive,
        duplicate_policy=config.input.duplicate_policy,
        self_loop_policy=config.input.self_loop_policy,
    )

    interim_dir: Path = state["interim_dir"]
    cleaned_path = interim_dir / "cleaned_hyperlinks.parquet"
    write_parquet_df(cleaned_df, cleaned_path)

    duration = time.time() - t0
    state["cleaned_df"] = cleaned_df
    state["clean_stats"] = stats
    state["cleaned_path"] = cleaned_path
    state["duration_02"] = duration
    return state


def stage_03_graph_build(config: EchoChamberConfig, state: dict[str, Any]) -> dict[str, Any]:
    """Stage 03: Directed & Undirected Graph Construction by Window."""
    t0 = time.time()
    logger.info("--- Stage 03: Graph Construction ---")
    cleaned_df: pd.DataFrame = state["cleaned_df"]
    window_graphs = {}

    for w_id, group in cleaned_df.groupby("window_id"):
        if len(group) < config.windows.min_event_count_for_analysis:
            logger.info("Skipping window %s with %d events (< %d)", w_id, len(group), config.windows.min_event_count_for_analysis)
            continue
        di_g = build_directed_graph(group, edge_weight=config.network.edge_weight)
        undir_g = project_undirected(di_g, projection_mode=config.network.detector_projection)
        window_graphs[w_id] = (di_g, undir_g)

    duration = time.time() - t0
    state["window_graphs"] = window_graphs
    state["duration_03"] = duration
    return state


def stage_04_community_detection(config: EchoChamberConfig, state: dict[str, Any]) -> dict[str, Any]:
    """Stage 04: Community Detection & Diagnostics."""
    t0 = time.time()
    logger.info("--- Stage 04: Community Detection ---")
    window_graphs = state["window_graphs"]
    window_communities: dict[str, dict[str, list[str]]] = {}
    window_node_to_comm: dict[str, dict[str, str]] = {}
    comm_records = []
    diagnostics = {}

    for w_id, (di_g, undir_g) in window_graphs.items():
        comms, n2c = detect_communities(
            undir_g,
            window_id=w_id,
            resolution=config.community_detection.resolution,
            seed=config.community_detection.seed,
            minimum_report_size=config.community_detection.minimum_report_size,
        )
        window_communities[w_id] = comms
        window_node_to_comm[w_id] = n2c

        diag = compute_network_diagnostics(di_g, undir_g, comms)
        diagnostics[w_id] = diag

        for cid, nodes in comms.items():
            for node in nodes:
                comm_records.append({
                    "window_id": w_id,
                    "community_id": cid,
                    "subreddit": node,
                })

    comm_df = pd.DataFrame(comm_records)
    run_dir: Path = state["run_dir"]
    comm_path = run_dir / "communities.parquet"
    write_parquet_df(comm_df, comm_path)

    duration = time.time() - t0
    state["window_communities"] = window_communities
    state["window_node_to_comm"] = window_node_to_comm
    state["diagnostics"] = diagnostics
    state["communities_df"] = comm_df
    state["communities_path"] = comm_path
    state["duration_04"] = duration
    return state


def stage_05_tracking(config: EchoChamberConfig, state: dict[str, Any]) -> dict[str, Any]:
    """Stage 05: Temporal Community Tracking."""
    t0 = time.time()
    logger.info("--- Stage 05: Temporal Tracking ---")
    window_communities = state["window_communities"]

    tracking_df, comm_to_track = track_communities_across_windows(
        window_communities,
        min_jaccard=config.tracking.min_jaccard,
        min_intersection=config.tracking.min_intersection,
        strategy=config.tracking.strategy,
    )

    run_dir: Path = state["run_dir"]
    tracking_path = run_dir / "tracking.parquet"
    write_parquet_df(tracking_df, tracking_path)

    duration = time.time() - t0
    state["tracking_df"] = tracking_df
    state["comm_to_track"] = comm_to_track
    state["tracking_path"] = tracking_path
    state["duration_05"] = duration
    return state


def stage_06_metrics(config: EchoChamberConfig, state: dict[str, Any]) -> dict[str, Any]:
    """Stage 06: Metrics Computation (I, H, D, S, ECI)."""
    t0 = time.time()
    logger.info("--- Stage 06: Metrics Computation ---")
    window_graphs = state["window_graphs"]
    window_communities = state["window_communities"]
    window_node_to_comm = state["window_node_to_comm"]
    comm_to_track = state["comm_to_track"]
    embedding_store: EmbeddingStore = state["embedding_store"]

    metrics_records = []

    for w_id, comms in window_communities.items():
        di_g, _ = window_graphs[w_id]
        n2c = window_node_to_comm[w_id]
        total_external_k = max(0, len(comms) - 1)

        for cid, nodes in comms.items():
            node_set = set(nodes)
            track_id = comm_to_track.get((w_id, cid), "T00000")

            # 1. Isolation
            iso, w_in, w_out = compute_isolation(di_g, node_set)

            # 2. Homogeneity
            hom, avg_cos, emb_count, cov = compute_community_homogeneity(
                node_set,
                embedding_store,
                minimum_coverage=config.metrics.homogeneity.minimum_coverage,
                minimum_embedded_nodes=config.metrics.homogeneity.minimum_embedded_nodes,
            )

            # 3. External Diversity & Exposure Scarcity
            div, scar, entropy, _ = compute_community_external_diversity(
                di_g,
                node_set,
                n2c,
                total_external_communities=total_external_k,
            )

            # 4. ECI
            eci_val, is_scorable = compute_eci(
                iso,
                hom,
                scar,
                w_isolation=config.eci.weights.isolation,
                w_homogeneity=config.eci.weights.homogeneity,
                w_scarcity=config.eci.weights.exposure_scarcity,
            )

            metrics_records.append({
                "window_id": w_id,
                "community_id": cid,
                "track_id": track_id,
                "node_count": len(nodes),
                "embedded_count": emb_count,
                "embedding_coverage": cov,
                "isolation": iso,
                "homogeneity": hom,
                "avg_cosine": avg_cos,
                "external_diversity": div,
                "exposure_scarcity": scar,
                "w_in": w_in,
                "w_out": w_out,
                "eci": eci_val,
                "scorable": is_scorable,
            })

    metrics_df = pd.DataFrame(metrics_records)
    run_dir: Path = state["run_dir"]
    metrics_path = run_dir / "metrics.parquet"
    write_parquet_df(metrics_df, metrics_path)

    duration = time.time() - t0
    state["metrics_df"] = metrics_df
    state["metrics_path"] = metrics_path
    state["duration_06"] = duration
    return state


def stage_07_baselines_null(config: EchoChamberConfig, state: dict[str, Any]) -> dict[str, Any]:
    """Stage 07: Baselines & Null Models."""
    t0 = time.time()
    logger.info("--- Stage 07: Baselines & Null Models ---")
    metrics_df = state["metrics_df"]
    embedding_store: EmbeddingStore = state["embedding_store"]
    window_communities = state["window_communities"]
    run_dir: Path = state["run_dir"]

    # 1. Baseline variants
    baselines_df = compute_baseline_variants(metrics_df)
    baselines_path = run_dir / "baselines.parquet"
    write_parquet_df(baselines_df, baselines_path)

    # 2. Null models for each window
    null_dfs = []
    for w_id, comms in window_communities.items():
        df_null = run_embedding_permutation_null(
            comms,
            embedding_store,
            num_permutations=config.analysis.null_permutations,
            seed=config.project.seed,
            minimum_coverage=config.metrics.homogeneity.minimum_coverage,
            minimum_embedded_nodes=config.metrics.homogeneity.minimum_embedded_nodes,
        )
        if not df_null.empty:
            df_null["window_id"] = w_id
            null_dfs.append(df_null)

    combined_null_df = pd.concat(null_dfs, ignore_index=True) if null_dfs else pd.DataFrame()
    null_path = run_dir / "null_model_results.parquet"
    write_parquet_df(combined_null_df, null_path)

    duration = time.time() - t0
    state["baselines_df"] = baselines_df
    state["null_df"] = combined_null_df
    state["baselines_path"] = baselines_path
    state["null_path"] = null_path
    state["duration_07"] = duration
    return state


def stage_08_sensitivity(config: EchoChamberConfig, state: dict[str, Any]) -> dict[str, Any]:
    """Stage 08: Sensitivity & Statistical Analysis."""
    t0 = time.time()
    logger.info("--- Stage 08: Sensitivity & Statistics ---")
    metrics_df = state["metrics_df"]
    window_graphs = state["window_graphs"]
    run_dir: Path = state["run_dir"]

    # 1. Resolution sweep
    res_df = run_resolution_sensitivity(
        window_graphs,
        resolutions=[0.8, 1.0, 1.2],
        seed=config.project.seed,
        minimum_report_size=config.community_detection.minimum_report_size,
    )
    res_path = run_dir / "sensitivity_resolution.parquet"
    write_parquet_df(res_df, res_path)

    # 2. Weight sensitivity
    weight_sens_df = run_weight_sensitivity(metrics_df)
    weight_sens_path = run_dir / "sensitivity_weights.parquet"
    write_parquet_df(weight_sens_df, weight_sens_path)

    # 3. Correlations
    corr_df = compute_spearman_correlations(metrics_df)
    corr_path = run_dir / "correlations.parquet"
    write_parquet_df(corr_df, corr_path)

    # 4. Bootstrap CI for ECI
    scorable_eci = metrics_df[metrics_df["scorable"] == True]["eci"].dropna()
    mean_val, ci_l, ci_u = compute_bootstrap_ci(
        scorable_eci,
        num_resamples=config.analysis.bootstrap_resamples,
        seed=config.analysis.bootstrap_seed,
    )
    logger.info("Bootstrap Mean ECI: %.4f (95%% CI: [%.4f, %.4f])", mean_val, ci_l, ci_u)

    duration = time.time() - t0
    state["duration_08"] = duration
    return state


def stage_09_reports_plots(config: EchoChamberConfig, state: dict[str, Any]) -> dict[str, Any]:
    """Stage 09: Summary Tables & Visualizations."""
    t0 = time.time()
    logger.info("--- Stage 09: Reports & Plots ---")
    run_dir: Path = state["run_dir"]
    metrics_df = state["metrics_df"]
    window_graphs = state["window_graphs"]
    window_communities = state["window_communities"]

    summary_dir = run_dir / "summary_tables"
    summary_dir.mkdir(parents=True, exist_ok=True)
    plots_dir = run_dir / "plots"
    plots_dir.mkdir(parents=True, exist_ok=True)

    # 1. Summary tables
    win_summary = generate_window_summary_table(metrics_df)
    export_safe_csv(win_summary, summary_dir / "window_summary.csv")

    top_echo = generate_top_echo_chambers_table(metrics_df, top_k=10)
    export_safe_csv(top_echo, summary_dir / "top_echo_chambers.csv")
    export_markdown_table(top_echo, summary_dir / "top_echo_chambers.md", title="Top Echo Chamber Communities")

    # 2. Static plots
    plot_eci_distribution(metrics_df, output_path=plots_dir / "eci_distribution.png")
    plot_isolation_vs_homogeneity(metrics_df, output_path=plots_dir / "isolation_vs_homogeneity.png")
    plot_temporal_trajectories(metrics_df, output_path=plots_dir / "temporal_trajectories.png")

    # 3. Community subgraph for the first window
    if window_graphs and window_communities:
        first_w = sorted(window_graphs.keys())[0]
        di_g, _ = window_graphs[first_w]
        comms = window_communities[first_w]
        plot_community_subgraph(di_g, comms, max_nodes=config.analysis.max_plot_nodes, output_path=plots_dir / "community_subgraph.png")

    # 4. Interactive HTML scatter
    create_interactive_scatter_html(metrics_df, plots_dir / "interactive_scatter.html")

    duration = time.time() - t0
    state["duration_09"] = duration
    return state
