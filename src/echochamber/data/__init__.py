"""Data module for downloading, parsing, cleaning, and windowing subreddit network data."""

from echochamber.data.clean import clean_hyperlinks
from echochamber.data.download import download_file, download_snap_datasets
from echochamber.data.embeddings import EmbeddingStore, parse_embeddings_file
from echochamber.data.fixtures import generate_synthetic_data
from echochamber.data.ingest import ingest_hyperlinks_tsv
from echochamber.data.schema import EMBEDDING_DIM, NORMALIZED_HYPERLINK_COLUMNS, RAW_HYPERLINK_COLUMNS
from echochamber.data.windows import assign_windows, generate_quarter_sequence, get_quarter_label, get_window_bounds

__all__ = [
    "EMBEDDING_DIM",
    "NORMALIZED_HYPERLINK_COLUMNS",
    "RAW_HYPERLINK_COLUMNS",
    "EmbeddingStore",
    "assign_windows",
    "clean_hyperlinks",
    "download_file",
    "download_snap_datasets",
    "generate_quarter_sequence",
    "generate_synthetic_data",
    "get_quarter_label",
    "get_window_bounds",
    "ingest_hyperlinks_tsv",
    "parse_embeddings_file",
]
