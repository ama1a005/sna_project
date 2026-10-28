"""Calendar quarter windowing logic and time-slice utilities."""

from datetime import datetime, timezone
import pandas as pd


def get_quarter_label(dt: datetime | pd.Timestamp) -> str:
    """Format a datetime into a calendar quarter label: YYYYQ# (e.g. '2014Q1')."""
    quarter = (dt.month - 1) // 3 + 1
    return f"{dt.year}Q{quarter}"


def generate_quarter_sequence(start_str: str, end_exclusive_str: str) -> list[str]:
    """Generate ordered list of quarter labels from start up to end_exclusive."""
    start_dt = pd.to_datetime(start_str, utc=True)
    end_dt = pd.to_datetime(end_exclusive_str, utc=True)

    quarters: list[str] = []
    current = start_dt
    while current < end_dt:
        label = get_quarter_label(current)
        if label not in quarters:
            quarters.append(label)
        # Advance by approximately 1 month to find next quarter boundaries accurately
        year = current.year + (1 if current.month > 9 else 0)
        month = ((current.month - 1) // 3 + 1) * 3 + 1
        if month > 12:
            month = 1
        current = pd.Timestamp(year=year, month=month, day=1, tz=timezone.utc)

    return sorted(quarters)


def assign_windows(
    df: pd.DataFrame,
    timestamp_col: str = "timestamp",
    window_col: str = "window_id",
) -> pd.DataFrame:
    """Parse timestamps to UTC and assign calendar quarter window IDs."""
    result = df.copy()
    ts = pd.to_datetime(result[timestamp_col], utc=True, errors="coerce", format="mixed")
    valid_mask = ts.notna()

    quarters = ts[valid_mask].dt.year.astype(str) + "Q" + ((ts[valid_mask].dt.month - 1) // 3 + 1).astype(str)
    result[window_col] = None
    result.loc[valid_mask, window_col] = quarters
    result[timestamp_col] = ts
    return result


def get_window_bounds(quarter_label: str) -> tuple[pd.Timestamp, pd.Timestamp]:
    """Return inclusive start and exclusive end timestamps for a given quarter (e.g. '2014Q1')."""
    year = int(quarter_label[:4])
    quarter = int(quarter_label[-1])

    start_month = (quarter - 1) * 3 + 1
    start_ts = pd.Timestamp(year=year, month=start_month, day=1, tz=timezone.utc)

    if quarter == 4:
        end_ts = pd.Timestamp(year=year + 1, month=1, day=1, tz=timezone.utc)
    else:
        end_ts = pd.Timestamp(year=year, month=start_month + 3, day=1, tz=timezone.utc)

    return start_ts, end_ts
