"""ECI ablation baselines and weight variants."""

import pandas as pd

BASELINE_VARIANTS = {
    "eci_equal": (1.0 / 3.0, 1.0 / 3.0, 1.0 / 3.0),
    "eci_topo_only": (0.5, 0.0, 0.5),
    "eci_content_only": (0.0, 1.0, 0.0),
    "eci_isolation_only": (1.0, 0.0, 0.0),
    "eci_scarcity_only": (0.0, 0.0, 1.0),
    "eci_content_heavy": (0.15, 0.70, 0.15),
    "eci_topo_heavy": (0.45, 0.10, 0.45),
}


def compute_baseline_variants(df: pd.DataFrame) -> pd.DataFrame:
    """Compute all 7 ECI ablation baselines on a metrics DataFrame.

    Requires columns: 'isolation', 'homogeneity', 'exposure_scarcity', 'scorable'.
    """
    res = df.copy()

    for name, (w_i, w_h, w_s) in BASELINE_VARIANTS.items():
        scores = []
        for _, row in res.iterrows():
            if not row.get("scorable", False):
                scores.append(None)
                continue

            iso = row.get("isolation")
            hom = row.get("homogeneity")
            sca = row.get("exposure_scarcity", 1.0)

            # If variant does not depend on homogeneity, allow scoring even if hom is None
            if w_h == 0.0 and iso is not None:
                val = w_i * iso + w_s * sca
            elif iso is not None and hom is not None:
                val = w_i * iso + w_h * hom + w_s * sca
            else:
                val = None

            if val is not None:
                val = max(0.0, min(1.0, float(val)))
            scores.append(val)

        res[name] = scores

    return res
