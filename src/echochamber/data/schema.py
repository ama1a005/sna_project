"""Data schemas, column names, and validation constants."""

RAW_HYPERLINK_COLUMNS = [
    "SOURCE_SUBREDDIT",
    "TARGET_SUBREDDIT",
    "POST_ID",
    "TIMESTAMP",
    "POST_LABEL",
    "PROPERTIES",
]

NORMALIZED_HYPERLINK_COLUMNS = [
    "source_subreddit",
    "target_subreddit",
    "post_id",
    "timestamp",
    "post_label",
    "properties",
]

EMBEDDING_DIM = 300

SNAP_DATASET_URLS = {
    "title": "https://snap.stanford.edu/data/soc-redditHyperlinks-title.tsv",
    "body": "https://snap.stanford.edu/data/soc-redditHyperlinks-body.tsv",
    "embeddings": "https://snap.stanford.edu/data/web-redditEmbeddings-subreddits.csv",
}
