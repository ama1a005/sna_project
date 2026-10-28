"""Deterministic synthetic dataset generator for testing and fixture runs.

# SYNTHETIC TEST DATA: All subreddits, hyperlinks, and embeddings generated herein
# are strictly synthetic and designated for testing and validation.
"""

from pathlib import Path
import numpy as np
import pandas as pd

from echochamber.data.schema import EMBEDDING_DIM
from echochamber.logging_utils import setup_logger

logger = setup_logger("echochamber.fixtures")


def generate_synthetic_data(
    output_dir: Path | str,
    seed: int = 42,
    num_quarters: int = 4,
    start_year: int = 2014,
) -> tuple[Path, Path]:
    """Generate deterministic synthetic hyperlinks TSV and embeddings CSV.

    Labels output clearly with SYNTHETIC TEST DATA notice.
    """
    out_dir = Path(output_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(seed)

    # Define communities and their subreddits
    clusters = {
        "tech": ["python", "datascience", "machinelearning", "programming", "compsci"],
        "gaming": ["games", "pcgaming", "nintendo", "playstation", "xbox"],
        "sports": ["soccer", "nba", "nfl", "baseball", "hockey"],
        "music": ["music", "hiphopheads", "indieheads", "metal", "electronicmusic"],
    }
    all_subreddits = [sub for cluster_subs in clusters.values() for sub in cluster_subs]

    # 1. Generate 300D Embeddings with cluster structure
    # Assign orthogonal/distinct base vectors to clusters
    cluster_centers: dict[str, np.ndarray] = {}
    for cluster_name in clusters:
        base = rng.normal(0, 1, size=EMBEDDING_DIM)
        cluster_centers[cluster_name] = base / np.linalg.norm(base)

    embeddings_dict: dict[str, np.ndarray] = {}
    for cluster_name, subs in clusters.items():
        center = cluster_centers[cluster_name]
        for sub in subs:
            # Leave one subreddit without embedding to test coverage
            if sub == "electronicmusic":
                continue
            noise = rng.normal(0, 0.15, size=EMBEDDING_DIM)
            v = center + noise
            embeddings_dict[sub] = v / np.linalg.norm(v)

    # Also add one zero-norm entry to test zero-norm filtering
    # and one malformed dimension row
    emb_rows: list[str] = [
        "# SYNTHETIC TEST DATA - Synthetic Subreddit 300D Embeddings",
    ]
    for sub, vec in embeddings_dict.items():
        vals_str = ",".join(f"{x:.6f}" for x in vec)
        emb_rows.append(f"{sub},{vals_str}")
    # Add zero-norm row for testing filter
    emb_rows.append("zero_norm_sub," + ",".join(["0.0"] * EMBEDDING_DIM))

    emb_file = out_dir / "fixture_embeddings.csv"
    with open(emb_file, "w", encoding="utf-8") as f:
        f.write("\n".join(emb_rows) + "\n")

    # 2. Generate Hyperlinks TSV
    hyperlink_rows: list[dict] = []
    post_counter = 1000

    quarter_starts = [
        (f"{start_year}-01-15 10:00:00", f"{start_year}Q1"),
        (f"{start_year}-04-15 10:00:00", f"{start_year}Q2"),
        (f"{start_year}-07-15 10:00:00", f"{start_year}Q3"),
        (f"{start_year}-10-15 10:00:00", f"{start_year}Q4"),
    ][:num_quarters]

    for q_idx, (base_ts, q_label) in enumerate(quarter_starts):
        dt_base = pd.to_datetime(base_ts, utc=True)

        for cluster_name, subs in clusters.items():
            # Internal links (within cluster)
            n_internal = rng.integers(25, 40)
            for _ in range(n_internal):
                src, tgt = rng.choice(subs, size=2, replace=True)
                post_counter += 1
                offset_days = rng.integers(0, 75)
                offset_seconds = rng.integers(0, 86400)
                ts = dt_base + pd.Timedelta(days=int(offset_days), seconds=int(offset_seconds))

                hyperlink_rows.append({
                    "SOURCE_SUBREDDIT": src,
                    "TARGET_SUBREDDIT": tgt,
                    "POST_ID": f"post_{post_counter}",
                    "TIMESTAMP": ts.strftime("%Y-%m-%d %H:%M:%S"),
                    "POST_LABEL": 1 if rng.random() > 0.1 else -1,
                    "PROPERTIES": "25,120,0.85,0.12",
                })

            # External links (to other clusters)
            n_external = rng.integers(5, 12)
            other_subs = [s for c, slist in clusters.items() if c != cluster_name for s in slist]
            for _ in range(n_external):
                src = rng.choice(subs)
                tgt = rng.choice(other_subs)
                post_counter += 1
                offset_days = rng.integers(0, 75)
                offset_seconds = rng.integers(0, 86400)
                ts = dt_base + pd.Timedelta(days=int(offset_days), seconds=int(offset_seconds))

                hyperlink_rows.append({
                    "SOURCE_SUBREDDIT": src,
                    "TARGET_SUBREDDIT": tgt,
                    "POST_ID": f"post_{post_counter}",
                    "TIMESTAMP": ts.strftime("%Y-%m-%d %H:%M:%S"),
                    "POST_LABEL": 1 if rng.random() > 0.1 else -1,
                    "PROPERTIES": "20,110,0.50,0.22",
                })

    # Add a duplicate row to test duplicate removal
    if hyperlink_rows:
        dup = dict(hyperlink_rows[0])
        hyperlink_rows.append(dup)

    tsv_file = out_dir / "fixture_hyperlinks.tsv"
    with open(tsv_file, "w", encoding="utf-8") as f:
        # Write comment header
        f.write("# SYNTHETIC TEST DATA - Stanford SNAP Hyperlinks Fixture\n")
        f.write("SOURCE_SUBREDDIT\tTARGET_SUBREDDIT\tPOST_ID\tTIMESTAMP\tPOST_LABEL\tPROPERTIES\n")
        for r in hyperlink_rows:
            f.write(
                f"{r['SOURCE_SUBREDDIT']}\t{r['TARGET_SUBREDDIT']}\t{r['POST_ID']}\t"
                f"{r['TIMESTAMP']}\t{r['POST_LABEL']}\t{r['PROPERTIES']}\n"
            )

    logger.info(
        "Generated synthetic fixture at %s: %d hyperlinks, %d embeddings",
        out_dir,
        len(hyperlink_rows),
        len(embeddings_dict),
    )
    return tsv_file, emb_file
