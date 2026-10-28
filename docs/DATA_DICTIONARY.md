# Data Dictionary & Schema Specification

## 1. Input Datasets

### Hyperlinks TSV (`soc-redditHyperlinks-*.tsv` / `fixture_hyperlinks.tsv`)
Tab-separated values representing hyperlink events between subreddits:
| Column Name | Type | Description | Policy / Transform |
| :--- | :--- | :--- | :--- |
| `SOURCE_SUBREDDIT` | String | Subreddit creating the post/hyperlink | Trimmed, casefolded |
| `TARGET_SUBREDDIT` | String | Subreddit referenced by hyperlink | Trimmed, casefolded |
| `POST_ID` | String | Unique Reddit post ID | Preserved |
| `TIMESTAMP` | String | UTC creation timestamp (`YYYY-MM-DD HH:MM:SS`) | Parsed to UTC `pd.Timestamp` |
| `POST_LABEL` | Integer | Sentiment label (`1` positive, `-1` negative) | Signed integer |
| `PROPERTIES` | String | Feature vector (length, sentiment vector) | Raw string |

### Embeddings CSV (`web-redditEmbeddings-subreddits.csv` / `fixture_embeddings.csv`)
Comma-separated values containing 300-dimensional continuous embeddings:
| Column | Type | Description | Policy / Transform |
| :--- | :--- | :--- | :--- |
| Column 0 | String | Subreddit identifier | Trimmed, casefolded |
| Columns 1..300 | Float | 300-dimensional Word2Vec coordinates | Unit L2 normalized: $z = v / \|v\|$ |

---

## 2. Output Artifacts

### Communities (`results/<run>/communities.parquet`)
| Column | Type | Description |
| :--- | :--- | :--- |
| `window_id` | String | Calendar quarter (e.g. `2014Q1`) |
| `community_id` | String | Formatted local ID: `{window_id}-C{index:04d}` |
| `subreddit` | String | Member subreddit name |

### Tracking (`results/<run>/tracking.parquet`)
| Column | Type | Description |
| :--- | :--- | :--- |
| `track_id` | String | Persistent trajectory ID: `T{index:05d}` |
| `window_id` | String | Current window ID |
| `community_id` | String | Current community ID |
| `prev_community_id` | String | Matched community ID in window $t-1$ (or `None`) |
| `jaccard_similarity` | Float | Node set Jaccard similarity with predecessor |
| `shared_nodes_count` | Integer | Intersection size $|C_t \cap C_{t-1}|$ |

### Metrics (`results/<run>/metrics.parquet`)
| Column | Type | Description |
| :--- | :--- | :--- |
| `window_id` | String | Window quarter |
| `community_id` | String | Local community ID |
| `track_id` | String | Persistent track ID |
| `node_count` | Integer | Member node count $|C|$ |
| `embedded_count` | Integer | Count of members with valid embeddings $|C_{\text{emb}}|$ |
| `embedding_coverage` | Float | Fraction $|C_{\text{emb}}| / |C|$ |
| `isolation` | Float | Outgoing volume boundary isolation $I(C) \in [0, 1]$ |
| `homogeneity` | Float | Semantic vector-sum cosine homogeneity $H(C) \in [0, 1]$ |
| `avg_cosine` | Float | Raw average pairwise cosine similarity $\in [-1, 1]$ |
| `external_diversity` | Float | Destination community entropy $D(C) \in [0, 1]$ |
| `exposure_scarcity` | Float | External exposure scarcity $S(C) = 1 - D \in [0, 1]$ |
| `w_in` | Float | Internal outgoing weight sum |
| `w_out` | Float | External outgoing weight sum |
| `eci` | Float | Echo Chamber Index $(I + H + S) / 3 \in [0, 1]$ |
| `scorable` | Boolean | True if community meets coverage and node count minimums |
