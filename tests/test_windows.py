"""Tests for calendar quarter windowing logic."""

import pandas as pd
import pytest

from echochamber.data.windows import (
    assign_windows,
    generate_quarter_sequence,
    get_quarter_label,
    get_window_bounds,
)


def test_get_quarter_label():
    """Verify quarter label generation."""
    ts1 = pd.to_datetime("2014-01-15 12:00:00", utc=True)
    ts2 = pd.to_datetime("2014-06-30 23:59:59", utc=True)
    ts3 = pd.to_datetime("2014-07-01 00:00:00", utc=True)
    ts4 = pd.to_datetime("2014-12-31 10:00:00", utc=True)

    assert get_quarter_label(ts1) == "2014Q1"
    assert get_quarter_label(ts2) == "2014Q2"
    assert get_quarter_label(ts3) == "2014Q3"
    assert get_quarter_label(ts4) == "2014Q4"


def test_generate_quarter_sequence():
    """Verify ordered sequence of quarters."""
    quarters = generate_quarter_sequence("2014-01-01T00:00:00Z", "2015-01-01T00:00:00Z")
    assert quarters == ["2014Q1", "2014Q2", "2014Q3", "2014Q4"]


def test_get_window_bounds():
    """Verify window boundary timestamps."""
    start, end = get_window_bounds("2014Q1")
    assert start == pd.Timestamp("2014-01-01 00:00:00+0000", tz="UTC")
    assert end == pd.Timestamp("2014-04-01 00:00:00+0000", tz="UTC")

    start4, end4 = get_window_bounds("2014Q4")
    assert start4 == pd.Timestamp("2014-10-01 00:00:00+0000", tz="UTC")
    assert end4 == pd.Timestamp("2015-01-01 00:00:00+0000", tz="UTC")


def test_assign_windows_dataframe():
    """Verify window ID assignment to DataFrame rows."""
    df = pd.DataFrame({
        "timestamp": ["2014-02-10 05:00:00", "2014-08-20 09:00:00", "invalid_date"]
    })
    result = assign_windows(df)
    assert result.iloc[0]["window_id"] == "2014Q1"
    assert result.iloc[1]["window_id"] == "2014Q3"
    assert pd.isna(result.iloc[2]["window_id"])
