"""Tests for statistical validation, bootstrap intervals, and config validation."""

import numpy as np
import pandas as pd
from pydantic import ValidationError
import pytest

from echochamber.analysis.statistics import compute_bootstrap_ci, compute_spearman_correlations
from echochamber.config import EchoChamberConfig, EciWeightsConfig


def test_config_validation_error_weights_not_summing_to_one():
    """Verify validation error if ECI weights don't sum to 1.0."""
    # Sum is 0.5 + 0.5 + 0.5 = 1.5 != 1.0
    with pytest.raises(ValidationError):
        EciWeightsConfig(isolation=0.5, homogeneity=0.5, exposure_scarcity=0.5)

    # Valid sum
    valid = EciWeightsConfig(isolation=0.4, homogeneity=0.3, exposure_scarcity=0.3)
    assert valid.isolation == 0.4


def test_spearman_correlations():
    """Verify Spearman correlation computation on paired variables."""
    df = pd.DataFrame({
        "isolation": [0.1, 0.4, 0.6, 0.8, 0.9],
        "homogeneity": [0.2, 0.3, 0.7, 0.85, 0.95],
        "exposure_scarcity": [0.1, 0.2, 0.5, 0.7, 0.8],
        "eci": [0.13, 0.3, 0.6, 0.78, 0.88],
    })

    corr_df = compute_spearman_correlations(df)
    assert not corr_df.empty
    # Monotonic relationship should yield high positive rho
    iso_hom = corr_df[(corr_df["var1"] == "isolation") & (corr_df["var2"] == "homogeneity")]
    assert float(iso_hom["spearman_rho"].iloc[0]) > 0.9


def test_bootstrap_confidence_interval():
    """Verify bootstrap CI bounds and mean preservation."""
    data = [0.4, 0.5, 0.6, 0.55, 0.45, 0.52]
    mean_val, ci_l, ci_u = compute_bootstrap_ci(data, num_resamples=100, seed=42)

    assert np.isclose(mean_val, np.mean(data))
    assert ci_l <= mean_val <= ci_u
    assert ci_l > 0.3
    assert ci_u < 0.7
