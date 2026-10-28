"""Atomic I/O utilities and CSV injection protection."""

import json
import os
import tempfile
from pathlib import Path
from typing import Any
import pandas as pd


def sanitize_cell_for_csv(val: Any) -> Any:
    """Prepend a single quote if string begins with unsafe formula prefixes (=, +, -, @)."""
    if isinstance(val, str) and len(val) > 0:
        if val[0] in ("=", "+", "-", "@"):
            return f"'{val}"
    return val


def export_safe_csv(df: pd.DataFrame, file_path: Path | str, index: bool = False) -> Path:
    """Export a DataFrame to CSV with formula injection defense and atomic write."""
    dest = Path(file_path).resolve()
    dest.parent.mkdir(parents=True, exist_ok=True)

    # Sanitize string columns
    safe_df = df.copy()
    for col in safe_df.select_dtypes(include=["object", "string"]).columns:
        safe_df[col] = safe_df[col].apply(sanitize_cell_for_csv)

    tmp_dir = dest.parent
    with tempfile.NamedTemporaryFile("w", dir=tmp_dir, delete=False, suffix=".tmp", encoding="utf-8") as f:
        tmp_name = f.name
        safe_df.to_csv(f, index=index)

    # Atomic rename (on Windows os.replace atomically overwrites if same filesystem)
    os.replace(tmp_name, dest)
    return dest


def atomic_write_text(content: str, file_path: Path | str, encoding: str = "utf-8") -> Path:
    """Write text content to file atomically."""
    dest = Path(file_path).resolve()
    dest.parent.mkdir(parents=True, exist_ok=True)

    tmp_dir = dest.parent
    with tempfile.NamedTemporaryFile("w", dir=tmp_dir, delete=False, suffix=".tmp", encoding=encoding) as f:
        tmp_name = f.name
        f.write(content)

    os.replace(tmp_name, dest)
    return dest


def atomic_write_json(data: Any, file_path: Path | str, indent: int = 2) -> Path:
    """Serialize and atomically write data as JSON."""
    content = json.dumps(data, indent=indent, default=str)
    return atomic_write_text(content, file_path)


def read_json(file_path: Path | str) -> Any:
    """Read and parse JSON from a file."""
    path = Path(file_path).resolve()
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def write_parquet_df(df: pd.DataFrame, file_path: Path | str) -> Path:
    """Write a DataFrame to Parquet format atomically."""
    dest = Path(file_path).resolve()
    dest.parent.mkdir(parents=True, exist_ok=True)

    tmp_dir = dest.parent
    with tempfile.NamedTemporaryFile("wb", dir=tmp_dir, delete=False, suffix=".tmp.parquet") as f:
        tmp_name = f.name

    df.to_parquet(tmp_name, engine="pyarrow", index=False)
    os.replace(tmp_name, dest)
    return dest


def read_parquet_df(file_path: Path | str) -> pd.DataFrame:
    """Read a Parquet file into a pandas DataFrame."""
    path = Path(file_path).resolve()
    return pd.read_parquet(path, engine="pyarrow")
