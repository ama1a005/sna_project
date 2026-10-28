"""Tests for embedding parsing, normalization, and zero-norm handling."""

from pathlib import Path
import numpy as np
import pytest

from echochamber.data.embeddings import parse_embeddings_file


def test_parse_embeddings_unit_normalization(temp_dir: Path):
    """Test that parsed embeddings are properly L2-normalized."""
    emb_file = temp_dir / "test_embeddings.csv"
    content = (
        "SubredditA,2.0,0.0,0.0\n"
        "SubredditB,0.0,5.0,0.0\n"
    )
    emb_file.write_text(content, encoding="utf-8")

    store = parse_embeddings_file(emb_file, expected_dim=3)
    assert len(store) == 2
    assert "subreddita" in store
    assert "SubredditB" in store

    vec_a = store.get("subreddita")
    assert vec_a is not None
    assert np.isclose(np.linalg.norm(vec_a), 1.0)
    assert np.allclose(vec_a, [1.0, 0.0, 0.0])


def test_parse_embeddings_zero_norm_excluded(temp_dir: Path):
    """Test that zero-norm vectors are excluded from embedding store."""
    emb_file = temp_dir / "zero_norm.csv"
    content = (
        "ValidSub,1.0,1.0,1.0\n"
        "ZeroSub,0.0,0.0,0.0\n"
    )
    emb_file.write_text(content, encoding="utf-8")

    store = parse_embeddings_file(emb_file, expected_dim=3)
    assert len(store) == 1
    assert "validsub" in store
    assert "zerosub" not in store


def test_calculate_coverage(temp_dir: Path):
    """Test embedding coverage fraction calculation."""
    emb_file = temp_dir / "coverage_test.csv"
    emb_file.write_text("sub1,1,0\nsub2,0,1\n", encoding="utf-8")
    store = parse_embeddings_file(emb_file, expected_dim=2)

    embedded, total, cov = store.calculate_coverage(["sub1", "sub2", "missing_sub", "another_missing"])
    assert total == 4
    assert embedded == 2
    assert np.isclose(cov, 0.5)
