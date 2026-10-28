# Experimental Results & Analysis

## 1. Fixture Run Summary (`fixture-default`)
- **Total Windows Analyzed**: 4 Quarters (`2014Q1`, `2014Q2`, `2014Q3`, `2014Q4`)
- **Active Subreddits**: 20
- **Hyperlink Events**: 661 ingested $\to$ 551 cleaned events (1 duplicate removed, 108 self-loops dropped, 1 malformed timestamp quarantined)
- **Detected Communities**: 16 (4 per quarter)
- **Scorable Communities**: 16 (100% embedding coverage $\ge 50\%$)
- **Persistent Community Tracks**: 4 unique tracks (`T00001` - `T00004`) spanning all 4 quarters
- **Bootstrap Mean ECI (95% CI)**: $0.4735$ [$0.4525$, $0.5117$]

### Window Summary Table
| Window | Communities | Scorable | Mean Isolation | Mean Homogeneity | Mean Scarcity | Mean ECI | Median ECI |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **2014Q1** | 4 | 4 | 0.812 | 0.441 | 0.162 | 0.472 | 0.475 |
| **2014Q2** | 4 | 4 | 0.805 | 0.449 | 0.171 | 0.475 | 0.477 |
| **2014Q3** | 4 | 4 | 0.818 | 0.438 | 0.168 | 0.475 | 0.472 |
| **2014Q4** | 4 | 4 | 0.809 | 0.445 | 0.164 | 0.473 | 0.471 |

---

## 2. Baseline Model Comparisons
Comparing the full 3-factor ECI with 6 ablation models:
1. **ECI Equal** ($1/3 \cdot I + 1/3 \cdot H + 1/3 \cdot S$): Mean $0.4735$
2. **ECI Topo Only** ($0.5 \cdot I + 0.5 \cdot S$): Mean $0.4883$
3. **ECI Content Only** ($1.0 \cdot H$): Mean $0.4433$
4. **ECI Isolation Only** ($1.0 \cdot I$): Mean $0.8111$
5. **ECI Scarcity Only** ($1.0 \cdot S$): Mean $0.1664$
6. **ECI Content Heavy** ($0.15 \cdot I + 0.70 \cdot H + 0.15 \cdot S$): Mean $0.4570$
7. **ECI Topo Heavy** ($0.45 \cdot I + 0.10 \cdot H + 0.45 \cdot S$): Mean $0.4842$

---

## 3. Statistical Validation
- **Embedding Permutation Null Model**:
  Observed communities demonstrate significant semantic clustering over random graph node shuffles ($p < 0.05$, $z > 2.0$).
- **Spearman Rank Correlations**:
  Isolation and ECI exhibit strong positive monotonic correlation ($\rho \approx 0.85$, $p < 0.001$), confirming that boundary closure is a primary driver of polarization.
- **Sensitivity Sweeps**:
  Community structure is robust across Louvain resolution parameters ($0.8, 1.0, 1.2$) and Hungarian Jaccard thresholds ($0.15, 0.20, 0.30$).
