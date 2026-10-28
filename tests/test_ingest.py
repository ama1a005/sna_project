"""Tests for hyperlink ingestion, quarantine, and cleaning."""

from pathlib import Path
import pandas as pd
import pytest

from echochamber.data.clean import clean_hyperlinks
from echochamber.data.ingest import ingest_hyperlinks_tsv


def test_ingest_hyperlinks_tsv_valid(temp_dir: Path):
    """Test valid ingestion of TSV file."""
    tsv_path = temp_dir / "sample.tsv"
    tsv_content = (
        "SOURCE_SUBREDDIT\tTARGET_SUBREDDIT\tPOST_ID\tTIMESTAMP\tPOST_LABEL\tPROPERTIES\n"
        "AskReddit\tIAMA\tpid1\t2014-01-01 10:00:00\t1\tprop1\n"
        "Python\tDataScience\tpid2\t2014-01-02 12:00:00\t-1\tprop2\n"
    )
    tsv_path.write_text(tsv_content, encoding="utf-8")

    df = ingest_hyperlinks_tsv(tsv_path)
    assert len(df) == 2
    assert list(df["source_subreddit"]) == ["askreddit", "python"]
    assert list(df["target_subreddit"]) == ["iama", "datascience"]
    assert list(df["post_label"]) == [1, -1]


def test_ingest_quarantine_invalid_rows(temp_dir: Path):
    """Test that malformed rows are properly quarantined."""
    tsv_path = temp_dir / "malformed.tsv"
    q_path = temp_dir / "quarantine.parquet"

    tsv_content = (
        "SOURCE_SUBREDDIT\tTARGET_SUBREDDIT\tPOST_ID\tTIMESTAMP\tPOST_LABEL\tPROPERTIES\n"
        "AskReddit\tIAMA\tpid1\t2014-01-01 10:00:00\t1\tprop1\n"
        "ShortLine\n"
        "\tMissingSource\tpid3\t2014-01-03 10:00:00\t1\tprop3\n"
    )
    tsv_path.write_text(tsv_content, encoding="utf-8")

    df = ingest_hyperlinks_tsv(tsv_path, quarantine_path=q_path)
    assert len(df) == 1
    assert q_path.exists()


def test_clean_hyperlinks_deduplication_and_self_loops():
    """Test deduplication and self-loop dropping."""
    raw_df = pd.DataFrame([
        {"source_subreddit": "sub1", "target_subreddit": "sub2", "post_id": "p1", "timestamp": "2014-01-01 10:00:00", "post_label": 1},
        {"source_subreddit": "sub1", "target_subreddit": "sub2", "post_id": "p1", "timestamp": "2014-01-01 10:00:00", "post_label": 1},  # duplicate
        {"source_subreddit": "sub1", "target_subreddit": "sub1", "post_id": "p2", "timestamp": "2014-01-01 11:00:00", "post_label": 1},  # self loop
        {"source_subreddit": "sub2", "target_subreddit": "sub3", "post_id": "p3", "timestamp": "2014-01-02 10:00:00", "post_label": 1},
    ])

    cleaned_df, stats = clean_hyperlinks(raw_df, duplicate_policy="same-post-source-target", self_loop_policy="drop-and-count")
    assert stats["duplicates_removed"] == 1
    assert stats["self_loops_dropped"] == 1
    assert len(cleaned_df) == 2
    assert "window_id" in cleaned_df.columns
    assert cleaned_df.iloc[0]["window_id"] == "2014Q1"
