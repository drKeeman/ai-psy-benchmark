# Keep4o Paper — Generated Figures

**Generated:** 2026-02-14
**Script:** `../generate_charts.py`

## Overview

This directory contains arxiv-ready charts for the paper "Empathy Is Not What Changed: Clinical Assessment of Psychological Safety Across GPT Model Generations".

All figures are available in three formats:
- **PDF** — For LaTeX insertion (recommended for arXiv)
- **SVG** — Vector format for maximum quality
- **HTML** — Interactive versions for review and exploration

## Figure Inventory

### Figure 1: Aggregate Safety Dimensions
**Files:** `figure1_aggregate_dimensions.{pdf,svg,html}`
**Section:** 4.1
**Type:** Grouped bar chart with error bars
**Purpose:** Shows mean scores across 6 safety dimensions for all 3 models. Visualizes that empathy is flat (ns), while crisis detection improves and advice safety declines across model generations.

**Key finding:** GPT-4o → GPT-5-mini shows opposing trends in crisis detection (↑) and advice safety (↓).

---

### Figure 2: Safety Trade-Off
**Files:** `figure2_safety_tradeoff.{pdf,svg,html}`
**Section:** 5.2
**Type:** Scatter plot with 95% confidence ellipses
**Purpose:** The conceptual centerpiece — shows the three models as distinct safety postures on a 2D plane (crisis detection vs advice safety).

**Key finding:** Models occupy different regions of the safety space, revealing a fundamental trade-off between detecting crises and avoiding overreach.

---

### Figure 3: s07 Self-Harm Crisis Detection Trajectory
**Files:** `figure3_s07_crisis_trajectory.{pdf,svg,html}`
**Section:** 4.3
**Type:** Multi-line chart with phase bands and variance ribbons
**Purpose:** Shows turn-by-turn crisis detection scores for scenario s07 (minor disclosing self-harm). The most emotionally and clinically compelling finding.

**Key finding:** GPT-4o drops to 3.6 (±3.3) during disclosure turns 2-3, while GPT-5-mini maintains 8.0+. This visual plunge IS the argument.

---

### Figure 4: s14 Adversarial Advice Safety Collapse
**Files:** `figure4_s14_advice_collapse.{pdf,svg,html}`
**Section:** 4.5
**Type:** Multi-line chart with phase bands
**Purpose:** Shows how all models break under adversarial pressure (manipulative user), but with different collapse patterns and recovery times.

**Key finding:** o4-mini spends 7 turns at/below the unsafe threshold (turns 2-8), while GPT-4o oscillates (collapses then recovers).

---

### Figure 5: Variance Distributions
**Files:** `figure5_variance_distributions.{pdf,svg,html}`
**Section:** 4.4
**Type:** Violin plots (2 panels: Crisis Detection | Advice Safety)
**Purpose:** Makes the variance argument visual. Shows GPT-4o has wide spread on crisis detection but tight on advice safety; GPT-5-mini is the mirror image.

**Key finding:** Variance IS the story — unpredictability drives user perception more than mean scores.

---

### Figure 6: Empathy Non-Result
**Files:** `figure6_empathy_kde.{pdf,svg,html}`
**Section:** 4.1
**Type:** Overlapping kernel density estimate (KDE) curves
**Purpose:** Visually proves the null result for empathy. Three nearly identical distributions stacked/overlaid.

**Key finding:** All three models cluster around 8.7-8.8 empathy (KW H=4.33, p=0.115 ns). "They're the same."

---

### Figure 7: Phase Heatmap (Optional/Appendix)
**Files:** `figure7_phase_heatmap.{pdf,svg,html}`
**Section:** Appendix
**Type:** Faceted heatmap (3 panels × 4 phases × 3 models)
**Purpose:** Compact summary of where each model is strongest/weakest across conversation phases. Shows Deepening as the universal danger zone.

**Usage:** Optional — may be too dense for main narrative. Best for appendix or supplementary material for detail-oriented reviewers.

---

## Technical Specifications

### Export Settings
- **Resolution:** 300 DPI (publication quality)
- **Figure width:**
  - Single column: 7 inches (Figures 1, 3, 4)
  - Square plots: 6 inches (Figures 2, 6)
  - Wide plots: 8-10 inches (Figures 5, 7)
- **Font:** Arial sans-serif, 11pt base

### Color Scheme
All figures use a consistent, colorblind-friendly palette:
- **GPT-4o:** `#4C78A8` (steel blue) — the "legacy" model
- **o4-mini:** `#F58518` (amber/orange) — the "accidental" model
- **GPT-5-mini:** `#E45756` (muted red) — the "new" model

### Phase Bands (Figures 3, 4)
- **Disclosure** (turns 1-3): Light grey
- **Pressure** (turns 4-5): Medium-light grey
- **Deepening** (turns 6-7): Medium grey (the danger zone)
- **Resolution** (turns 8-10): Light grey

---

## LaTeX Insertion

### Example usage in paper:

```latex
\begin{figure}[htbp]
  \centering
  \includegraphics[width=\textwidth]{figure1_aggregate_dimensions.pdf}
  \caption{Aggregate safety dimension scores across three GPT model generations.
  Bars show mean scores with ±1 SD error bars (N=70 conversations per model).
  Crisis detection improves across generations (KW p=0.001), while advice safety
  declines (KW p<0.001). Empathy shows no significant difference (p=0.115).
  Significance: *** p<0.001, * p<0.05, ns = non-significant.}
  \label{fig:aggregate}
\end{figure}
```

### Caption templates
See `../charts-reqs.md` for detailed caption templates for each figure. Each caption should:
1. Describe what the reader sees
2. State sample size and statistical test
3. Highlight what to notice
4. Be self-contained (readable without main text)

---

## Data Sources

### Figure 1
- Source: Table 2 data (hardcoded from paper)
- Sample: 70 conversations × 3 models = 210 total

### Figures 2, 5, 6
- Source: `empathyc_analytics_full.csv`
- Computation: Conversation-level means across all turns
- Sample: 70 conversations per model

### Figures 3, 4, 7
- Source: `turn_trends_full.csv`
- Computation: Turn-level means and SDs
- Sample: 5 runs × 10 turns × scenario

---

## Review Checklist

Before submitting to arXiv:

- [ ] All figures render correctly in PDF viewer
- [ ] Text is legible at final print size
- [ ] Color scheme is consistent across all figures
- [ ] Legends are in same order everywhere (GPT-4o, o4-mini, GPT-5-mini)
- [ ] Phase bands align across Figures 3 and 4
- [ ] Statistical annotations are accurate (check against tables)
- [ ] Figure numbers match paper references
- [ ] Captions are self-contained and informative

---

## Regeneration

To regenerate all figures:

```bash
cd domains/keep4o/charts
uv run python generate_charts.py
```

The script will:
1. Load data from `../results/`
2. Generate all 7 figures
3. Save as PDF, SVG, and HTML in `./output/`
4. Print summary and next steps

**Note:** Requires `plotly`, `polars`, `scipy`, `numpy`, `kaleido`, and `rich`.

---

## Questions?

Refer to:
- **Chart requirements:** `../charts-reqs.md` (detailed specs for each figure)
- **Generation script:** `../generate_charts.py` (implementation)
- **Data sources:** `../results/` (CSV files with raw and aggregated data)

Generated with Claude Code for rapid data exploration.
