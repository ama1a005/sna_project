# Research Methodology & Mathematical Formulations

## 1. Network Topology & Temporal Windowing
Online social network interactions are framed as directed, weighted temporal graphs:
$$G_t = (V_t, E_t, W_t)$$
where time is discretized into calendar quarters (e.g. `2014Q1`, `2014Q2`).
- A node $u \in V_t$ represents a subreddit.
- A directed edge $(u, v) \in E_t$ represents a hyperlink embedded in a post from source subreddit $u$ referencing target subreddit $v$.
- The weight $W_t(u, v)$ is the cumulative count of deduplicated hyperlink events within window $t$.

## 2. Community Detection & Partitioning
Partitions are uncovered on the undirected symmetric projection:
$$w(u, v) = W_t(u, v) + W_t(v, u)$$
using Louvain modularity maximization:
$$Q = \frac{1}{2m} \sum_{i,j} \left[ A_{ij} - \frac{k_i k_j}{2m} \right] \delta(c_i, c_j)$$
Louvain resolution parameter $\gamma$ defaults to 1.0 (with sensitivity sweeps over $0.8, 1.0, 1.2$).
To ensure reproducibility:
- Nodes are sorted alphabetically before graph construction.
- Seed is pinned to 42.
- Communities are ranked deterministically by descending size and smallest node name, assigned local IDs `{window_id}-C{index:04d}`.

## 3. Three-Factor Echo Chamber Index (ECI)

### 3.1 Topological Boundary Isolation $I(C, t)$
Quantifies the degree to which outgoing communication is captured within the community boundary:
$$I(C, t) = \frac{W_{\text{in}}(C)}{W_{\text{in}}(C) + W_{\text{out}}(C)}$$
where:
$$W_{\text{in}}(C) = \sum_{u \in C, v \in C} w(u, v)$$
$$W_{\text{out}}(C) = \sum_{u \in C, v \notin C} w(u, v)$$
If $W_{\text{in}} + W_{\text{out}} == 0$, $I(C, t)$ is undefined (`None`).

### 3.2 Semantic Embedding Homogeneity $H(C)$
Computed over 300-dimensional unit L2-normalized embeddings $z_u = \frac{v_u}{\|v_u\|}$.
Using the vector-sum identity:
$$\left\|\sum_{u=1}^m z_u\right\|^2 = \sum_{u=1}^m \|z_u\|^2 + \sum_{u \ne v} \langle z_u, z_v \rangle = m + m(m-1) \cdot \text{avg\_cos}$$
Solving for average cosine similarity:
$$\text{avg\_cos} = \frac{\left\|\sum_{u=1}^m z_u\right\|^2 - m}{m(m - 1)}$$
This operates in $O(m \cdot d)$ time and memory rather than $O(m^2 \cdot d)$.
Homogeneity is mapped to the unit interval $[0, 1]$:
$$H(C) = \frac{\text{avg\_cos} + 1}{2}$$
If embedding coverage $|C_{\text{emb}}| / |C| < \text{minimum\_coverage}$ (e.g. 0.5) or $m < 2$, $H(C)$ is `None`.

### 3.3 External Exposure Diversity $D(C, t)$ & Scarcity $S(C, t)$
For outgoing links outside $C$, let $p_j = \frac{W(C \to C_j)}{W_{\text{out}}}$ be the probability distribution over external destination communities:
$$E(C) = -\sum_{j, p_j > 0} p_j \ln(p_j)$$
$$D(C) = \frac{E(C)}{\ln(K_{\text{possible}})}$$
$$S(C) = 1 - D(C)$$
Degeneracy handling:
- If $W_{\text{out}} == 0 \implies D = 0.0, S = 1.0$.
- If $K_{\text{possible}} \le 0 \implies D = 0.0, S = 1.0$.
- If $K_{\text{possible}} == 1$ and $W_{\text{out}} > 0 \implies D = 1.0, S = 0.0$.

### 3.4 Combined Index (ECI)
$$\text{ECI}(C, t) = w_I \cdot I(C, t) + w_H \cdot H(C) + w_S \cdot S(C, t)$$
Default weights: $w_I = w_H = w_S = 1/3$.
If $I(C, t)$ or $H(C)$ is `None`, $\text{ECI}$ is `None` (unscorable).

## 4. Longitudinal Tracking: Hungarian Matching
To establish community continuity across sequential quarters $t$ and $t+1$:
1. Pairwise Jaccard similarity between node sets:
   $$J(C_t, C_{t+1}) = \frac{|C_t \cap C_{t+1}|}{|C_t \cup C_{t+1}|}$$
2. An edge is eligible if $J \ge 0.20$ and $|C_t \cap C_{t+1}| \ge 2$.
3. Matching is solved via the Hungarian algorithm (`scipy.optimize.linear_sum_assignment`) with cost $1.0 - J$.
4. Matched communities inherit track ID `T{index:05d}`. Unmatched communities initialize a new track ID.

## 5. Signed Sentiment Stratification & Hostility-Weighted Isolation (Novel Contribution)

Existing echo chamber literature treats network edges as unpolarized interaction conduits. To distinguish genuine echo chambers from general controversy hubs or outward outrage machines, we incorporate edge polarity from the Stanford SNAP dataset (`POST_LABEL` $\in \{-1, +1\}$), where $+1$ denotes positive/neutral sentiment and $-1$ denotes hostile/negative sentiment.

### 5.1 Sentiment Ratios
For a community $C$ at quarter $t$, outgoing hyperlink flows are partitioned into internal and external channels:
$$SR_{\text{internal}}(C, t) = \frac{P_{\text{in}}(C, t)}{P_{\text{in}}(C, t) + N_{\text{in}}(C, t)}$$
$$SR_{\text{external}}(C, t) = \frac{P_{\text{out}}(C, t)}{P_{\text{out}}(C, t) + N_{\text{out}}(C, t)}$$
where $P_{\text{in}}, N_{\text{in}}$ denote counts of positive and negative internal hyperlinks within $C$, and $P_{\text{out}}, N_{\text{out}}$ denote outgoing positive and negative hyperlinks targeting subreddits outside $C$. If total outgoing flow in either channel is zero, the respective ratio is undefined (`None`).

### 5.2 Sentiment Asymmetry $SA(C, t)$
Measures the directional divergence between intra-community warmth and inter-community antagonism:
$$SA(C, t) = SR_{\text{internal}}(C, t) - SR_{\text{external}}(C, t)$$
- **$SA > 0$ (Echo Chamber Polarity)**: The community maintains high internal cohesion and positivity, while directing hostility primarily toward external communities (classic ingroup favoritism and outgroup derogation).
- **$SA < 0$ (Inverted Sentiment)**: The community is internally adversarial or self-critical, while projecting positive or deferential sentiment outward.
- **$SA \approx 0$ (Sentiment Neutrality)**: Uniform sentiment distribution regardless of community boundaries.

### 5.3 Hostility-Weighted Isolation $HI(C, t)$
To integrate signed polarity directly into topological boundary measurement, we parameterize boundary permeability by hostility:
- Internal links receive weight $1.0$ if positive and $0.5$ if negative (discounting internal conflict as boundary leakage).
- External links receive weight $1.0$ if negative and $0.5$ if positive (treating external attacks as primary vectors of inter-group polarization).

$$\tilde{W}_{\text{in}}(C) = 1.0 \cdot P_{\text{in}} + 0.5 \cdot N_{\text{in}}$$
$$\tilde{W}_{\text{out}}(C) = 0.5 \cdot P_{\text{out}} + 1.0 \cdot N_{\text{out}}$$
$$HI(C, t) = \frac{\tilde{W}_{\text{in}}(C)}{\tilde{W}_{\text{in}}(C) + \tilde{W}_{\text{out}}(C)}$$
If $\tilde{W}_{\text{in}} + \tilde{W}_{\text{out}} == 0$, $HI(C, t)$ is undefined (`None`).
Hostility-Weighted Isolation systematically elevates the echo-chamber classification of communities that exhibit insular solidarity paired with aggressive external posturing.
