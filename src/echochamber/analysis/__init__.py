"""Analysis module: Baselines, Null models, Sensitivity, Statistics, and Tables."""

from echochamber.analysis.baselines import BASELINE_VARIANTS, compute_baseline_variants
from echochamber.analysis.null_models import run_embedding_permutation_null
from echochamber.analysis.report_tables import (
    export_markdown_table,
    generate_top_echo_chambers_table,
    generate_window_summary_table,
)
from echochamber.analysis.sensitivity import run_resolution_sensitivity, run_weight_sensitivity
from echochamber.analysis.statistics import compute_bootstrap_ci, compute_spearman_correlations

__all__ = [
    "BASELINE_VARIANTS",
    "compute_baseline_variants",
    "compute_bootstrap_ci",
    "compute_spearman_correlations",
    "export_markdown_table",
    "generate_top_echo_chambers_table",
    "generate_window_summary_table",
    "run_embedding_permutation_null",
    "run_resolution_sensitivity",
    "run_weight_sensitivity",
]
