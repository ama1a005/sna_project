"""Page 5: Methodology - Formal Definitions, Architecture & Citations."""

import streamlit as st

st.set_page_config(page_title="Methodology - Echo Chamber", page_icon="📖", layout="wide")

from app.components import render_header

render_header("Methodological Framework & Mathematical Formulation", "Formal mathematical definitions and pipeline architecture")

st.markdown("""
### 1. Network Construction & Temporal Windowing
The online social network is modeled as a sequence of directed weighted graphs $G_t = (V_t, E_t, W_t)$ over non-overlapping calendar quarters (e.g. 2014Q1):
- Vertices $u \\in V_t$: active subreddits posting hyperlinks.
- Directed edge $(u, v) \\in E_t$: hyperlink originating from $u$ pointing to $v$.
- Weight $W_t(u, v)$: count of unique post events linking $u$ to $v$.

### 2. Louvain Community Detection
Communities are identified on the undirected projection $G'_t$ where $w(u, v) = W_t(u, v) + W_t(v, u)$ by optimizing modularity:
$$Q = \\frac{1}{2m} \\sum_{i,j} \\left[ A_{ij} - \\frac{k_i k_j}{2m} \\right] \\delta(c_i, c_j)$$

### 3. Three-Factor Echo Chamber Index (ECI)
The Echo Chamber Index combines topological boundary closure, semantic alignment, and external interaction diversity:

#### A. Topological Isolation $I(C, t)$
Quantifies the fraction of outbound communication retained internally:
$$I(C, t) = \\frac{W_{\\text{in}}(C)}{W_{\\text{in}}(C) + W_{\\text{out}}(C)}$$
Where $W_{\\text{in}} = \\sum_{u, v \\in C} w(u, v)$ and $W_{\\text{out}} = \\sum_{u \\in C, v \\notin C} w(u, v)$.

#### B. Embedding Homogeneity $H(C)$
Calculated over unit L2-normalized 300-dimensional embeddings $\\{z_u\\}_{u \\in C_{\\text{emb}}}$ using the $O(m \\cdot d)$ vector-sum identity:
$$\\text{avg\\_cos} = \\frac{\\left\\|\\sum_{u=1}^m z_u\\right\\|^2 - m}{m(m - 1)}$$
$$H(C) = \\frac{\\text{avg\\_cos} + 1}{2}$$

#### C. External Exposure Scarcity $S(C, t)$
Measures the concentration of external links across candidate external communities. With $p_j = W(C \\to C_j) / W_{\\text{out}}$:
$$E(C) = -\\sum_{j, p_j > 0} p_j \\ln(p_j)$$
$$D(C) = \\frac{E(C)}{\\ln(K_{\\text{possible}})}$$
$$S(C) = 1 - D(C)$$

#### D. Echo Chamber Index
$$\\text{ECI}(C, t) = w_I \\cdot I(C, t) + w_H \\cdot H(C) + w_S \\cdot S(C, t)$$
Default weights: $w_I = w_H = w_S = \\frac{1}{3}$.

### 4. Longitudinal Community Tracking
Communities are linked across consecutive quarters $t$ and $t+1$ using the Hungarian matching algorithm on Jaccard similarity:
$$J(C_t, C_{t+1}) = \\frac{|C_t \\cap C_{t+1}|}{|C_t \\cup C_{t+1}|}$$
Subject to minimum thresholds: $J \\ge 0.20$ and $|C_t \\cap C_{t+1}| \\ge 2$.

### 5. Dataset Attribution
- **Stanford SNAP Reddit Hyperlink Network**:
  Kumar et al., *Community Interaction and Conflict on the Web*, WWW 2018.
- **Stanford SNAP Subreddit Embeddings**:
  300-dimensional continuous vector representations generated via Word2Vec over subreddit comment co-occurrences.
""")
