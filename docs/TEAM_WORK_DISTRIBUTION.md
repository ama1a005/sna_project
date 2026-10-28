# 23CSE356 Social Network Analysis — Project Work Distribution & Viva Defense Guide

**Project Title:** Temporal Echo Chamber Detection in Online Social Networks  
**Dataset:** Stanford SNAP Reddit Hyperlink Network & Subreddit Embeddings (858,454 links, 55,863 subreddits, 14 Quarters)  
**Repository:** https://github.com/ama1a005/sna_project.git  

---

## 👥 Executive Role Summary (Who Says What in Front of Ma'am)

| Role | Person | Focus Area | Key Modules Owned |
| :--- | :--- | :--- | :--- |
| **Person A** | Data Ingestion, Dynamic Graph Modeling & Community Detection | Graph Theory, SNAP Cleaning, Louvain Modularity, Quarterly Windows | `data/`, `graph/build.py`, `graph/partitions.py`, `test_graph.py`, `test_windows.py` |
| **Person B** | Core Mathematical Formulations (ECI Index) & Longitudinal Tracking | Multi-factor ECI ($I, H, D, S$), Vector-Sum Optimization, Hungarian Tracking | `metrics/isolation.py`, `metrics/homogeneity.py`, `metrics/diversity.py`, `metrics/eci.py`, `graph/tracking.py` |
| **Person C** | Research Novelty (Signed Sentiment), Ablations, Experiments & UI | Sentiment Asymmetry ($SA$), 7 Baseline Models, Permutation Nulls, Streamlit | `metrics/sentiment.py`, `analysis/`, `pipeline/`, `app/` (all 6 pages), `test_sentiment.py` |

---

## 📘 Person A: Data Engineering & Network Graph Architecture

### 1. Official Responsibility Description
> *"I designed and implemented the data processing pipeline and the temporal graph construction engine. I parsed Stanford SNAP's 858,454 raw directed hyperlinks across 14 quarters (2014Q1–2017Q2), handled deduplication on `(source, target, post_id)` triples, and projected the directed graph into an undirected symmetric representation for Louvain community detection."*

### 2. Files You Must Study
1. [`src/echochamber/data/ingest.py`](file:///C:/Users/amala/.gemini/antigravity/scratch/temporal-echo-chambers/src/echochamber/data/ingest.py) — TSV parsing, quarantine logic, timestamp validation.
2. [`src/echochamber/data/clean.py`](file:///C:/Users/amala/.gemini/antigravity/scratch/temporal-echo-chambers/src/echochamber/data/clean.py) — Deduplication policy and self-loop dropping.
3. [`src/echochamber/data/windows.py`](file:///C:/Users/amala/.gemini/antigravity/scratch/temporal-echo-chambers/src/echochamber/data/windows.py) — Assigning UTC timestamps to calendar quarters (`[start, end)` half-open intervals).
4. [`src/echochamber/data/embeddings.py`](file:///C:/Users/amala/.gemini/antigravity/scratch/temporal-echo-chambers/src/echochamber/data/embeddings.py) — Parsing 51,269 300-dimensional vector representations and zero-norm exclusions.
5. [`src/echochamber/graph/build.py`](file:///C:/Users/amala/.gemini/antigravity/scratch/temporal-echo-chambers/src/echochamber/graph/build.py) — Creating NetworkX directed graphs (`DiGraph`) with edge weights and sentiment tallies, plus symmetric undirected projection ($W(\{u,v\}) = w(u,v) + w(v,u)$).
6. [`src/echochamber/graph/partitions.py`](file:///C:/Users/amala/.gemini/antigravity/scratch/temporal-echo-chambers/src/echochamber/graph/partitions.py) — Seeded Louvain modularity clustering and community ID formatting (`2014Q1-C0001`).
7. [`docs/DATA_DICTIONARY.md`](file:///C:/Users/amala/.gemini/antigravity/scratch/temporal-echo-chambers/docs/DATA_DICTIONARY.md) — Exact data column schemas.

### 3. Likely Questions From Ma'am & Your Exact Answers
- **Q1: Why did you project the directed graph to an undirected one for Louvain?**  
  *Answer:* Standard Louvain community detection optimizes modularity based on symmetric adjacency. However, we strictly preserve the directed graph (`DiGraph`) with full edge directions and weights so Person B can compute directional isolation ($W_{in}$ vs $W_{out}$) and external destination entropy.
- **Q2: Why deduplicate on `(source, target, post_id)` instead of just `post_id`?**  
  *Answer:* A single Reddit post can hyperlink multiple different destination subreddits in its body. Deduplicating on `post_id` alone would improperly discard genuine outgoing cross-community interactions.
- **Q3: How did you ensure deterministic Louvain results across runs?**  
  *Answer:* In `graph/partitions.py`, we sort subreddit node names lexicographically prior to graph construction and lock the random seed to `42`.

---

## 📙 Person B: Quantitative Metrics & Longitudinal Community Tracking

### 1. Official Responsibility Description
> *"I formulated and implemented the multi-dimensional Echo Chamber Index (ECI) combining structural isolation, posting-behavior embedding homogeneity, and exposure scarcity. I optimized the homogeneity computation from $O(m^2 \cdot d)$ to $O(m \cdot d)$ using vector-sum identities, and developed the Hungarian bipartite matching algorithm to track communities longitudinally across quarters."*

### 2. Files You Must Study
1. [`src/echochamber/metrics/isolation.py`](file:///C:/Users/amala/.gemini/antigravity/scratch/temporal-echo-chambers/src/echochamber/metrics/isolation.py) — Formula:
   $$I(C, t) = \frac{W_{\text{in}}}{W_{\text{in}} + W_{\text{out}}}$$
2. [`src/echochamber/metrics/homogeneity.py`](file:///C:/Users/amala/.gemini/antigravity/scratch/temporal-echo-chambers/src/echochamber/metrics/homogeneity.py) — $O(m \cdot d)$ vector-sum cosine formula:
   $$\text{avg\_cos} = \frac{\left\|\sum_{u=1}^m z_u\right\|^2 - m}{m(m - 1)}, \quad H(C) = \frac{\text{avg\_cos} + 1}{2}$$
3. [`src/echochamber/metrics/diversity.py`](file:///C:/Users/amala/.gemini/antigravity/scratch/temporal-echo-chambers/src/echochamber/metrics/diversity.py) — Destination Shannon Entropy $E$, normalized diversity $D = E / \ln(K_{\text{possible}})$, and Exposure Scarcity $S = 1 - D$.
4. [`src/echochamber/metrics/eci.py`](file:///C:/Users/amala/.gemini/antigravity/scratch/temporal-echo-chambers/src/echochamber/metrics/eci.py) — Configurable composite metric:
   $$\text{ECI} = w_I \cdot I + w_H \cdot H + w_S \cdot S$$
5. [`src/echochamber/graph/tracking.py`](file:///C:/Users/amala/.gemini/antigravity/scratch/temporal-echo-chambers/src/echochamber/graph/tracking.py) — Hungarian one-to-one matching on Jaccard node overlap ($J \ge 0.2, \text{intersection} \ge 2$) assigning persistent Track IDs (`T00001`).
6. [`tests/test_metrics.py`](file:///C:/Users/amala/.gemini/antigravity/scratch/temporal-echo-chambers/tests/test_metrics.py) & [`tests/test_tracking.py`](file:///C:/Users/amala/.gemini/antigravity/scratch/temporal-echo-chambers/tests/test_tracking.py) — Exact numerical unit tests.

### 3. Likely Questions From Ma'am & Your Exact Answers
- **Q1: How does your vector-sum trick avoid the quadratic pairwise comparison?**  
  *Answer:* Summing all pairwise dot products $\sum_{u \ne v} z_u \cdot z_v$ equals $\|\sum z_u\|^2 - \sum \|z_u\|^2$. Since vectors are unit-normalized, $\sum \|z_u\|^2 = m$. Thus we compute the sum vector in $O(m \cdot d)$ time and its squared norm in $O(d)$ time, bypassing the $O(m^2 \cdot d)$ pairwise matrix.
- **Q2: What is the crucial scientific limitation of SNAP subreddit embeddings?**  
  *Answer:* The 300D embeddings are static, whole-period vectors generated over the entire 2014–2017 timeline. Therefore, changes in community homogeneity over time reflect *membership and composition shifts*, not real-time semantic evolution or viewpoint drift.
- **Q3: What happens to ECI when a community has zero outgoing hyperlinks?**  
  *Answer:* If $W_{\text{in}} + W_{\text{out}} = 0$, $I$ is undefined (`None`). We enforce that missing factors render ECI unscorable rather than silently imputing zero.

---

## 📕 Person C: Research Novelty, Statistical Ablations & Dashboard Architecture

### 1. Official Responsibility Description
> *"I designed the novel signed sentiment isolation metric, which distinguishes affirmative echo chambers from hostile outrage machines using hyperlink sentiment polarity (`POST_LABEL`). I also implemented the 7 baseline ablation models, the embedding permutation null hypothesis testing, sensitivity analysis sweeps, and the interactive Streamlit dashboard."*

### 2. Files You Must Study
1. [`src/echochamber/metrics/sentiment.py`](file:///C:/Users/amala/.gemini/antigravity/scratch/temporal-echo-chambers/src/echochamber/metrics/sentiment.py) — **Our Original Novelty:**
   - Sentiment Ratio ($SR = P / (P+N)$)
   - Sentiment Asymmetry ($SA = SR_{\text{internal}} - SR_{\text{external}}$)
   - Hostility-Weighted Isolation ($HI$)
2. [`src/echochamber/analysis/baselines.py`](file:///C:/Users/amala/.gemini/antigravity/scratch/temporal-echo-chambers/src/echochamber/analysis/baselines.py) — The 7 baseline models: Full ECI, Topology-only ($I+S$), Content-only ($H$), Isolation-only ($I$), Scarcity-only ($S$), Content-heavy, and Topology-heavy.
3. [`src/echochamber/analysis/null_models.py`](file:///C:/Users/amala/.gemini/antigravity/scratch/temporal-echo-chambers/src/echochamber/analysis/null_models.py) — Shuffling embedding vectors among active nodes across 100 iterations to calculate empirical $p$-values.
4. [`src/echochamber/analysis/sensitivity.py`](file:///C:/Users/amala/.gemini/antigravity/scratch/temporal-echo-chambers/src/echochamber/analysis/sensitivity.py) — Louvain resolution sweeps ($0.8, 1.0, 1.2$) and weight variations.
5. [`app/Home.py`](file:///C:/Users/amala/.gemini/antigravity/scratch/temporal-echo-chambers/app/Home.py) & [`app/pages/`](file:///C:/Users/amala/.gemini/antigravity/scratch/temporal-echo-chambers/app/pages/) — The 6-page interactive Streamlit dashboard, especially `6_Sentiment_Analysis.py` and `4_Comparisons.py`.
6. [`docs/RESULTS.md`](file:///C:/Users/amala/.gemini/antigravity/scratch/temporal-echo-chambers/docs/RESULTS.md) — Real empirical numbers (Mean ECI = 0.8200, 993 scorable groups).

### 3. Likely Questions From Ma'am & Your Exact Answers
- **Q1: What is your project's novel contribution beyond prior literature?**  
  *Answer:* Standard SNA echo chamber literature only examines link counts or modularity. We introduced **Sentiment Asymmetry ($SA$)** using the signed `POST_LABEL` field. A community with high isolation but equal sentiment inside and outside is just isolated; a community with $SA > 0$ (friendly inside, aggressive outside) exhibits true echo chamber insularity.
- **Q2: Why are ablations necessary if you have the ECI formula?**  
  *Answer:* We evaluated 7 ablation variants on identical community cohorts to prove that structural isolation ($I$), semantic homogeneity ($H$), and destination scarcity ($S$) provide orthogonal, non-redundant information (Spearman $\rho$ between $I$ and $H$ is $0.64$).
- **Q3: What do the permutation null models prove?**  
  *Answer:* By shuffling embedding vectors across graph nodes 100 times while preserving graph topology and community sizes, we proved that observed within-community homogeneity is significantly higher than chance ($p < 0.01$).

---

## 🎯 Quick Presentation Script (3-Minute Group Flow)

1. **Person A speaks first (1 min):**  
   *"Good morning Ma'am. Our project analyzes temporal echo chambers across 858,454 Reddit hyperlinks and 55,863 subreddits from 2014 to 2017. My role was data engineering, temporal partitioning across 14 calendar quarters, and constructing both directed interaction graphs and symmetric projections for Louvain community detection."*
2. **Person B speaks second (1 min):**  
   *"Building on those detected communities, my responsibility was formulating the Echo Chamber Index. I combined Structural Isolation, Embedding Homogeneity using an $O(m \cdot d)$ vector-sum identity, and Destination Exposure Scarcity based on Shannon Entropy. I also built the Hungarian matching algorithm to track how communities evolve, split, or merge over time."*
3. **Person C speaks third (1 min):**  
   *"To address a key gap in existing literature, I designed our research novelty: Signed Sentiment Asymmetry, which verifies whether isolated communities behave hostily toward outside communities. I also evaluated 7 ablation baselines, permutation null models, and developed the interactive 6-page Streamlit dashboard to visualize longitudinal trajectories."*
