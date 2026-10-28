# Limitations & Ethical Considerations

## 1. Algorithmic Limitations
1. **Static Community Detection per Slice**:
   Louvain is executed independently per calendar quarter, relying on Hungarian post-hoc matching rather than online dynamic modularity tracking (e.g. evolutionary clustering).
2. **Missing Embedding Coverage**:
   Niche or newly formed subreddits may lack precomputed Word2Vec embeddings in the static SNAP embedding file. Communities with $< 50\%$ coverage are conservatively marked unscorable.
3. **Sentiment Polarity Handling**:
   In the default topology configuration (`negative_label_handling: ignore_sign_for_topology`), edge existence and volume denote interaction regardless of sentiment polarity (+1 vs -1). Negative interactions (conflicts/brigading) are treated as structural links.

## 2. Computational & Data Considerations
1. **Discretization Granularity**:
   Quarterly discretization (`calendar_quarter`) balances edge density and computational efficiency, but smooths over sub-quarter political or cultural events (e.g. week-long controversies).
2. **Pre-2018 Static Embeddings**:
   SNAP subreddit embeddings represent static semantic representations across the entire Reddit history up to 2017, meaning dynamic semantic drift of terms is not modeled.

## 3. Ethical Considerations
- Subreddit-level public communication: analysis is strictly conducted on community-level public hyperlinks, preserving individual user privacy.
- Formula injection protection (`'=`, `'+`, `'-`, `'@`) is enforced on all exported tabular reports.
