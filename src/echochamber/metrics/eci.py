"""Three-factor Echo Chamber Index (ECI) calculation."""

from typing import Tuple


def compute_eci(
    isolation: float | None,
    homogeneity: float | None,
    exposure_scarcity: float | None,
    w_isolation: float = 1.0 / 3.0,
    w_homogeneity: float = 1.0 / 3.0,
    w_scarcity: float = 1.0 / 3.0,
) -> tuple[float | None, bool]:
    """Calculate the Echo Chamber Index (ECI).

    Formula:
        ECI = w_I * I + w_H * H + w_S * S

    Conditions:
        If isolation is None or homogeneity is None, community is unscorable -> ECI is None.
        If exposure_scarcity is None, defaults to 1.0 (assuming complete lack of exposure).

    Returns:
        (eci_score, is_scorable)
    """
    if isolation is None or homogeneity is None:
        return None, False

    s = exposure_scarcity if exposure_scarcity is not None else 1.0

    eci = w_isolation * isolation + w_homogeneity * homogeneity + w_scarcity * s
    eci = max(0.0, min(1.0, float(eci)))
    return eci, True
