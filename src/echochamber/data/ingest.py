"""TSV hyperlink ingestion, quarantine handling, and name normalization."""

import csv
from pathlib import Path
import pandas as pd

from echochamber.data.schema import NORMALIZED_HYPERLINK_COLUMNS
from echochamber.logging_utils import setup_logger
from echochamber.storage.io import write_parquet_df

logger = setup_logger("echochamber.ingest")


def ingest_hyperlinks_tsv(
    file_path: Path | str,
    quarantine_path: Path | str | None = None,
    name_policy: str = "strip-and-casefold",
) -> pd.DataFrame:
    """Ingest a SNAP hyperlinks TSV file, normalize columns and names, and quarantine invalid rows.

    Returns:
        DataFrame with normalized columns:
        [source_subreddit, target_subreddit, post_id, timestamp, post_label, properties]
    """
    path = Path(file_path).resolve()
    if not path.exists():
        raise FileNotFoundError(f"Hyperlinks file does not exist: {path}")

    logger.info("Ingesting hyperlinks from %s", path)

    valid_rows: list[dict] = []
    quarantine_rows: list[dict] = []

    with open(path, "r", encoding="utf-8", errors="replace") as f:
        reader = csv.reader(f, delimiter="\t")
        header = next(reader, None)
        if not header:
            return pd.DataFrame(columns=NORMALIZED_HYPERLINK_COLUMNS)

        # Map header case-insensitively
        col_map = {col.strip().upper(): i for i, col in enumerate(header)}
        src_idx = col_map.get("SOURCE_SUBREDDIT", 0)
        tgt_idx = col_map.get("TARGET_SUBREDDIT", 1)
        pid_idx = col_map.get("POST_ID", 2)
        ts_idx = col_map.get("TIMESTAMP", 3)
        lbl_idx = col_map.get("POST_LABEL", 4)
        prop_idx = col_map.get("PROPERTIES", 5)

        for line_num, parts in enumerate(reader, 2):
            if len(parts) < 4:
                quarantine_rows.append({"line_num": line_num, "reason": "too_few_columns", "raw": "\t".join(parts)})
                continue

            src = parts[src_idx].strip()
            tgt = parts[tgt_idx].strip()
            pid = parts[pid_idx].strip() if len(parts) > pid_idx else ""
            ts_str = parts[ts_idx].strip() if len(parts) > ts_idx else ""
            lbl_str = parts[lbl_idx].strip() if len(parts) > lbl_idx else "1"
            prop_str = parts[prop_idx].strip() if len(parts) > prop_idx else ""

            if not src or not tgt or not ts_str:
                quarantine_rows.append({"line_num": line_num, "reason": "missing_required_fields", "raw": "\t".join(parts)})
                continue

            if name_policy == "strip-and-casefold":
                src = src.casefold()
                tgt = tgt.casefold()

            try:
                label_val = int(lbl_str)
            except ValueError:
                label_val = 1

            valid_rows.append({
                "source_subreddit": src,
                "target_subreddit": tgt,
                "post_id": pid,
                "timestamp": ts_str,
                "post_label": label_val,
                "properties": prop_str,
            })

    logger.info("Parsed %d valid rows, %d quarantined rows from %s", len(valid_rows), len(quarantine_rows), path.name)

    if quarantine_path and quarantine_rows:
        q_path = Path(quarantine_path).resolve()
        q_path.parent.mkdir(parents=True, exist_ok=True)
        q_df = pd.DataFrame(quarantine_rows)
        write_parquet_df(q_df, q_path)
        logger.warning("Quarantined %d malformed rows to %s", len(quarantine_rows), q_path)

    return pd.DataFrame(valid_rows, columns=NORMALIZED_HYPERLINK_COLUMNS)
