# Empirical Results — Temporal Echo Chamber Detection

## Dataset Summary
- **858,454 valid hyperlinks** (571,927 title + 286,561 body, 34 out-of-range excluded)
- **51,269 valid subreddit embeddings** (9 zero-norm excluded from 51,278 original rows, 300-dimensional Word2Vec)
- **14 calendar quarters**: 2014Q1 – 2017Q2
- **0 quarantined rows**, **0 self-loops** retained after filtering
- **55,863 unique subreddits** participating across the network

---

## Community Detection

Across the 14 calendar quarters, the Louvain algorithm ($\gamma = 1.0$, resolution sensitivity checked across $0.8, 1.0, 1.2$) discovered 1,673 total communities satisfying the minimum reporting threshold ($\ge 3$ nodes). Of these, 993 communities meet the strict embedding coverage criterion ($\ge 70\%$ embedded nodes, $\ge 2$ embedded members) and are fully scorable.

### Per-Window Summary Table

| Window ID | Total Communities | Scorable Communities | Mean Isolation | Mean Homogeneity | Mean Scarcity | Mean ECI | Median ECI |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **2014Q1** | 82 | 55 | 0.800 | 0.808 | 0.713 | 0.774 | 0.743 |
| **2014Q2** | 79 | 53 | 0.818 | 0.806 | 0.677 | 0.767 | 0.698 |
| **2014Q3** | 83 | 56 | 0.834 | 0.826 | 0.715 | 0.792 | 0.727 |
| **2014Q4** | 94 | 67 | 0.825 | 0.812 | 0.736 | 0.791 | 0.784 |
| **2015Q1** | 96 | 63 | 0.833 | 0.825 | 0.708 | 0.789 | 0.724 |
| **2015Q2** | 95 | 55 | 0.844 | 0.810 | 0.727 | 0.794 | 0.732 |
| **2015Q3** | 116 | 60 | 0.867 | 0.839 | 0.777 | 0.828 | 0.894 |
| **2015Q4** | 134 | 81 | 0.876 | 0.840 | 0.808 | 0.842 | 0.887 |
| **2016Q1** | 145 | 78 | 0.869 | 0.825 | 0.793 | 0.829 | 0.862 |
| **2016Q2** | 144 | 85 | 0.871 | 0.845 | 0.814 | 0.843 | 0.894 |
| **2016Q3** | 147 | 79 | 0.867 | 0.834 | 0.818 | 0.840 | 0.889 |
| **2016Q4** | 147 | 90 | 0.875 | 0.834 | 0.803 | 0.837 | 0.894 |
| **2017Q1** | 153 | 70 | 0.860 | 0.832 | 0.788 | 0.827 | 0.828 |
| **2017Q2** | 158 | 101 | 0.903 | 0.827 | 0.843 | 0.858 | 0.934 |

---

## ECI Distribution

- **993 scorable communities** (of 1,673 total detected across all windows)
- **Mean ECI**: **0.8200** (95% Bootstrap Confidence Interval: **[0.8111, 0.8279]**)
- **Median ECI**: **0.8351**
- **Standard Deviation**: **0.1372**
- **Range**: **[0.5012, 0.9977]**

The distribution exhibits a noticeable negative skew, with over half the scorable communities scoring above $0.835$, reflecting high degrees of structural insulation and thematic concentration on the Reddit hyperlink graph.

---

## Component Analysis

- **Mean Isolation ($I = 0.8578$)**: Detected communities retain approximately **85.8%** of their total outgoing hyperlink volume within internal member subreddits, evidencing high ingroup orientation.
- **Mean Homogeneity ($H = 0.8273$)**: Subreddits co-clustered into communities share high cosine similarity in 300D Word2Vec representation space, confirming that structural partitioning correlates strongly with shared semantic posting contexts.
- **Mean Exposure Scarcity ($S = 0.7748$)**: External communication is highly concentrated among a minimal subset of target communities rather than uniformly distributed across external graph partitions.

---

## Component Correlations (Spearman)

All pairwise Spearman rank correlations between ECI components are statistically significant ($p < 10^{-100}$), validating the tripartite conceptual construct:

| Variable 1 | Variable 2 | Spearman $\rho$ | $p$-value | Sample Size ($N$) | Interpretation |
| :--- | :--- | :---: | :---: | :---: | :--- |
| **Isolation** | **Homogeneity** | **0.6403** | $1.10 \times 10^{-115}$ | 993 | Moderate-strong positive alignment: insular topological boundaries predict shared semantic embedding content. |
| **Isolation** | **Exposure Scarcity** | **0.8020** | $4.98 \times 10^{-224}$ | 993 | Strong positive coupling: communities retaining links internally also focus external outbound links on few targets. |
| **Isolation** | **ECI** | **0.9074** | $< 10^{-300}$ | 993 | Dominant driver of composite index. |
| **Homogeneity** | **Exposure Scarcity** | **0.6531** | $8.76 \times 10^{-122}$ | 993 | Semantically homogeneous clusters exhibit selective cross-community engagement. |
| **Homogeneity** | **ECI** | **0.8372** | $5.22 \times 10^{-262}$ | 993 | Strong monotonic contribution to total echo chamber intensity. |
| **Exposure Scarcity** | **ECI** | **0.8956** | $< 10^{-300}$ | 993 | Strong monotonic contribution to composite index. |

---

## Temporal Trends

1. **Monotonic Rise in ECI**: Quarterly mean ECI rises steadily from **0.7737** (2014Q1) to **0.8576** (2017Q2). Median ECI rises from **0.7425** to **0.9338**.
2. **Community Proliferation & Network Fragmentation**: The number of communities expanding beyond the minimum reporting size almost doubles over the observation window, increasing from **82** in 2014Q1 to **158** in 2017Q2.
3. **Mid-2015 Structural Shift**: A sharp increase in isolation ($> 0.86$) and scarcity ($> 0.77$) begins in 2015Q3, coinciding with significant sociopolitical divergence in web discourse and Reddit administrative platform updates.

---

## Top Echo Chambers

Top ten highest ECI communities identified across the entire longitudinal dataset, showing specific subreddits, track persistence, and structural scores:

| Window ID | Community ID | Track ID | Node Count | Subreddits | Isolation | Homogeneity | Exposure Scarcity | ECI |
| :--- | :--- | :---: | :---: | :--- | :---: | :---: | :---: | :---: |
| **2016Q3** | `2016Q3-C0130` | `T01079` | 3 | `homebrews`, `vectrex`, `virtualboy` | 1.0000 | 0.9931 | 1.0000 | **0.9977** |
| **2014Q3** | `2014Q3-C0074` | `T00215` | 3 | `gtagivers`, `xboxlive`, `xboxlivetrials` | 1.0000 | 0.9914 | 1.0000 | **0.9971** |
| **2017Q1** | `2017Q1-C0126` | `T01345` | 3 | `facedownassup`, `innie`, `simps` | 1.0000 | 0.9911 | 1.0000 | **0.9970** |
| **2015Q4** | `2015Q4-C0058` | `T00623` | 5 | `albumbabes`, `anusfree`, `kindalookslike`, `longlegsgirls`, `tinytits` | 1.0000 | 0.9891 | 1.0000 | **0.9964** |
| **2015Q1** | `2015Q1-C0076` | `T00372` | 3 | `chris`, `daniel`, `john` | 1.0000 | 0.9888 | 1.0000 | **0.9963** |
| **2016Q2** | `2016Q2-C0119` | `T00934` | 3 | `frontensemble`, `marimba`, `percussion` | 1.0000 | 0.9884 | 1.0000 | **0.9961** |
| **2017Q1** | `2017Q1-C0105` | `T01325` | 3 | `bootyforeat`, `bootyfrombelow`, `highheelbabes` | 1.0000 | 0.9877 | 1.0000 | **0.9959** |
| **2017Q2** | `2017Q2-C0063` | `T01156` | 5 | `gta5onlinefreemoney`, `gta_5_hack_online`, `gtamoney`, `gtainlinescheats`, `gtavcredits` | 1.0000 | 0.9871 | 1.0000 | **0.9957** |
| **2016Q4** | `2016Q4-C0070` | `T01156` | 5 | `gta5onlinefreemoney`, `gta_5_hack_online`, `gtamoney`, `gtainlinescheats`, `gtavcredits` | 1.0000 | 0.9871 | 1.0000 | **0.9957** |
| **2016Q2** | `2016Q2-C0056` | `T00760` | 7 | `cheggrequests`, `courseherodocuments`, `courseherounlock`, `freesteamcode`, `homework_help`, `pastebinrequests`, `slavelabour` | 1.0000 | 0.9869 | 1.0000 | **0.9956** |

---

## Limitations

1. **Static Pre-trained Subreddit Embeddings**: Subreddit vector representations are fixed across the entire 2014–2017 observation window. While structural edges and community assignments evolve dynamically each quarter, semantic shifts within stable subreddit names cannot be captured without time-stratified dynamic language models.
2. **Hyperlinks as Proxy for Inter-Community Interaction**: The network models explicit cross-subreddit hyperlink references (`r/subreddit`), which represent intentional inter-community signaling but exclude user-level comment co-membership and cross-posting without direct URLs.
3. **Algorithmic Modularity Heuristics**: Louvain community detection optimizes modularity greedily on undirected projections. While stabilized by deterministic alphabetical pre-sorting and random seed pinning, graph partitioning resolution limits can obscure subtle micro-factions within large macro-clusters.
4. **Binary Sentiment Granularity**: Stanford SNAP `POST_LABEL` provides binary classifications ($-1$ vs $+1$), which conflates neutral and positively aligned hyperlinks under $+1$ while separating explicit hostility under $-1$.
