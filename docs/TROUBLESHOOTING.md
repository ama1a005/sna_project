# Troubleshooting Guide

## 1. Network Download Errors (Errno 11001 / Connection Timeout)
- **Cause**: Sandboxed environment, proxy restrictions, or offline execution blocking downloads from `snap.stanford.edu`.
- **Solution**:
  - For offline evaluation or testing, run fixture mode: `echochamber run --config configs/fixture.yaml`.
  - To use SNAP data when network is permitted, run `echochamber download --raw-dir data/raw` outside sandboxed restrictions.
  - Or manually place the three files into `data/raw/`:
    - `soc-redditHyperlinks-title.tsv`
    - `soc-redditHyperlinks-body.tsv`
    - `web-redditEmbeddings-subreddits.csv`

## 2. Memory Exhaustion During Homogeneity Computation
- **Cause**: Using naive $O(m^2 \cdot d)$ pairwise cosine loops on large communities.
- **Solution**: `echochamber` uses the $O(m \cdot d)$ vector-sum formula:
  $$\text{avg\_cos} = \frac{\|\sum z_u\|^2 - m}{m(m-1)}$$
  which scales linearly with community size and requires minimal memory.

## 3. Matplotlib Cache Warnings on Windows
- **Cause**: Matplotlib attempting to write to read-only `C:\Users\amala\.matplotlib`.
- **Solution**: Handled automatically in `echochamber/__init__.py` by setting `MPLCONFIGDIR` to a writable system temp subdirectory (`tempfile.gettempdir() / "echochamber_mpl"`).

## 4. Weight Validation Errors
- **Cause**: ECI weights (`isolation`, `homogeneity`, `exposure_scarcity`) not summing to $1.0$.
- **Solution**: Ensure the three floating-point values in your config YAML sum to $1.0$ within tolerance $10^{-5}$ (e.g. `0.3333333333333333, 0.3333333333333333, 0.3333333333333334`).
