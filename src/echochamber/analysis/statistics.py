"""Statistical checks: Spearman rank correlation and bootstrap confidence intervals."""

import numpy as np
import pandas as pd
from scipy.stats import spearmanr


def compute_spearman_correlations(
    df: pd.DataFrame,
    columns: list[str] | None = None,
) -> pd.DataFrame:
    """Compute pairwise Spearman rank correlation coefficients and p-values."""
    cols = columns or ["isolation", "homogeneity", "exposure_scarcity", "eci"]
    valid_cols = [c for c in cols if c in df.columns]

    # Filter to complete rows
    clean_df = df[valid_cols].dropna()

    records = []
    for i in range(len(valid_cols)):
        for j in range(i + 1, len(valid_cols)):
            c1, c2 = valid_cols[i], valid_cols[j]
            if len(clean_df) >= 3:
                res = spearmanr(clean_df[c1], clean_df[c2])
                rho, p_val = float(res.statistic), float(res.pvalue)
            else:
                rho, p_val = 0.0, 1.0

            records.append({
                "var1": c1,
                "var2": c2,
                "spearman_rho": rho,
                "p_value": p_val,
                "sample_size": len(clean_df),
            })

    return pd.DataFrame(records)


def compute_bootstrap_ci(
    data: list[float] | np.ndarray | pd.Series,
    num_resamples: int = 200,
    confidence_level: float = 0.95,
    seed: int = 142,
) -> tuple[float, float, float]:
    """Compute bootstrap confidence interval for the sample mean.

    Returns:
        (mean, ci_lower, ci_upper)
    """
    arr = np.array([x for x in data if x is not None and not np.isnan(x)], dtype=np.float64)
    if len(arr) == 0:
        return 0.0, 0.0, 0.0

    if len(arr) == 1:
        v = float(arr[0])
        return v, v, v

    rng = np.random.default_rng(seed)
    boot_means = np.empty(num_resamples, dtype=np.float64)
    n = len(arr)

    for i in range(num_resamples):
        sample = rng.choice(arr, size=n, replace=True)
        boot_means[i] = np.mean(sample)

    alpha = 1.0 - confidence_level
    lower_pct = (alpha / 2.0) * 100.0
    upper_pct = (1.0 - alpha / 2.0) * 100.0

    ci_lower = float(np.percentile(boot_means, lower_pct))
    ci_upper = float(np.percentile(boot_means, upper_pct))
    mean_val = float(np.mean(arr))

    return mean_val, ci_lower, ci_upper
