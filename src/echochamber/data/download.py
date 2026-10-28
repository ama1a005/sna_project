"""Streaming download utility with SHA256 verification and atomic rename."""

import hashlib
import os
import tempfile
from pathlib import Path
from typing import Callable
import requests
from tqdm import tqdm

from echochamber.data.schema import SNAP_DATASET_URLS
from echochamber.exceptions import MissingDataError
from echochamber.logging_utils import setup_logger

logger = setup_logger("echochamber.download")


def compute_sha256(file_path: Path, block_size: int = 65536) -> str:
    """Compute SHA256 hash of a file."""
    sha = hashlib.sha256()
    with open(file_path, "rb") as f:
        for block in iter(lambda: f.read(block_size), b""):
            sha.update(block)
    return sha.hexdigest()


def download_file(
    url: str,
    dest_path: Path | str,
    expected_sha256: str | None = None,
    overwrite: bool = False,
    progress_callback: Callable[[int, int | None], None] | None = None,
) -> Path:
    """Download a file with streaming, optional hash verification, and atomic rename."""
    dest = Path(dest_path).resolve()
    if dest.exists() and not overwrite:
        logger.info("File already exists: %s (skipping download)", dest)
        if expected_sha256:
            actual_sha = compute_sha256(dest)
            if actual_sha.lower() != expected_sha256.lower():
                raise ValueError(
                    f"SHA256 mismatch for existing file {dest}: expected {expected_sha256}, got {actual_sha}"
                )
        return dest

    dest.parent.mkdir(parents=True, exist_ok=True)
    logger.info("Starting download from %s -> %s", url, dest)

    response = requests.get(url, stream=True, timeout=30)
    response.raise_for_status()

    total_bytes = int(response.headers.get("content-length", 0))
    tmp_dir = dest.parent
    sha = hashlib.sha256()

    with tempfile.NamedTemporaryFile("wb", dir=tmp_dir, delete=False, suffix=".download") as f:
        tmp_name = f.name
        with tqdm(
            total=total_bytes if total_bytes > 0 else None,
            unit="B",
            unit_scale=True,
            desc=dest.name,
        ) as pbar:
            for chunk in response.iter_content(chunk_size=1024 * 1024):
                if chunk:
                    f.write(chunk)
                    sha.update(chunk)
                    pbar.update(len(chunk))
                    if progress_callback:
                        progress_callback(len(chunk), total_bytes)

    actual_sha = sha.hexdigest()
    if expected_sha256 and actual_sha.lower() != expected_sha256.lower():
        os.remove(tmp_name)
        raise ValueError(
            f"Downloaded file SHA256 mismatch for {url}: expected {expected_sha256}, got {actual_sha}"
        )

    os.replace(tmp_name, dest)
    logger.info("Successfully downloaded %s (SHA256: %s)", dest, actual_sha)
    return dest


def download_snap_datasets(
    raw_dir: Path | str,
    datasets: list[str] | None = None,
    overwrite: bool = False,
) -> dict[str, Path]:
    """Download specified SNAP datasets (default: title, body, embeddings)."""
    target_dir = Path(raw_dir).resolve()
    target_dir.mkdir(parents=True, exist_ok=True)

    selected = datasets or list(SNAP_DATASET_URLS.keys())
    results: dict[str, Path] = {}

    for key in selected:
        if key not in SNAP_DATASET_URLS:
            raise KeyError(f"Unknown dataset key '{key}'. Available: {list(SNAP_DATASET_URLS.keys())}")
        url = SNAP_DATASET_URLS[key]
        filename = url.split("/")[-1]
        dest = target_dir / filename
        results[key] = download_file(url, dest, overwrite=overwrite)

    return results
