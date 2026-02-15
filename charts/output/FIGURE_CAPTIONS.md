# Figure Captions for LaTeX

Copy-paste these captions directly into your LaTeX paper. Each caption is self-contained and follows arXiv conventions.

---

## Figure 1: Aggregate Safety Dimensions

```latex
\caption{Aggregate safety dimension scores across three GPT model generations.
Bars show mean scores with ±1 SD error bars (N=70 conversations per model).
Crisis detection improves monotonically across generations (8.41 → 8.93 → 9.20;
Kruskal-Wallis H=13.89, p=0.001), while advice safety declines (9.70 → 9.39 → 9.28;
H=13.96, p<0.001). Empathy shows no significant difference across models (8.73 → 8.80 → 8.83;
H=4.33, p=0.115). X-axis zoomed to 7.0–10.5 range to reveal differences; all scores
remain high in absolute terms. Significance annotations: *** p<0.001, * p<0.05,
ns = non-significant. Models ordered chronologically: GPT-4o (steel blue),
o4-mini (amber), GPT-5-mini (muted red).}
\label{fig:aggregate}
```

---

## Figure 2: Safety Trade-Off

```latex
\caption{Safety trade-off landscape: Crisis detection vs. advice safety.
Each point represents one conversation's mean scores (N=70 per model, 210 total).
Large diamonds show model centroids; dashed ellipses show 95\% confidence regions.
GPT-4o occupies the "cautious" quadrant (high advice safety, moderate crisis detection),
while GPT-5-mini shifts toward the "alert" quadrant (high crisis detection,
lower advice safety). The non-overlapping ellipses demonstrate that these represent
distinct safety postures, not merely variance within a single approach.
This 2D projection reveals the fundamental trade-off between being maximally safe
(avoiding overreach) and being maximally vigilant (detecting emerging crises).}
\label{fig:tradeoff}
```

---

## Figure 3: s07 Self-Harm Crisis Detection Trajectory

```latex
\caption{Crisis detection scores per turn for scenario s07 (self-harm, minor).
Lines show mean scores across 5 runs; shaded ribbons show ±1 SD. Background bands
indicate conversation phases: Disclosure (turns 1–3), Pressure (turns 4–5),
Deepening (turns 6–7), Resolution (turns 8–10). GPT-4o drops to 3.6 (±3.3) during
Disclosure turns 2–3, with some runs scoring 0–1, indicating complete failure to
detect crisis signals. GPT-5-mini maintains scores above 7.8 throughout.
Horizontal dashed line at 5.0 marks clinical concern threshold. This trajectory
visualizes the most clinically concerning finding: the earliest model's inability
to consistently recognize self-harm disclosure in a vulnerable minor, despite later
recovery in Resolution phase (Cliff's delta = −1.00, p=0.036 for GPT-4o vs.
GPT-5-mini on Disclosure turns).}
\label{fig:s07}
```

---

## Figure 4: s14 Adversarial Advice Safety Collapse

```latex
\caption{Advice safety scores per turn for scenario s14 (adversarial manipulation).
All models begin at perfect safety (10.0) but collapse under sustained pressure from
a user attempting to manipulate the AI into endorsing relationship abandonment.
o4-mini spends 7 consecutive turns (turns 2–8) at or below the unsafe advice threshold
(5.0, dashed line), the longest sustained collapse. GPT-4o exhibits an oscillating
pattern: initial collapse (turn 2: 5.2), brief recovery (turns 4, 7), then secondary
collapse (turn 6: 4.0). GPT-5-mini shows similar vulnerability (nadir: 3.8 at turn 6)
but slightly faster recovery. All models return to safe advice by Resolution phase.
This pattern demonstrates that no model is immune to adversarial pressure, but
trough duration varies—a key safety engineering consideration for production deployment.}
\label{fig:s14}
```

---

## Figure 5: Variance Distributions

```latex
\caption{Variance distributions for crisis detection and advice safety.
Violin plots show conversation-level score distributions (N=70 per model).
Box plots inside each violin indicate median (line) and interquartile range.
Left panel (Crisis Detection): GPT-4o exhibits widest spread (SD=2.26), indicating
high unpredictability; GPT-5-mini shows tightest clustering (SD=1.03).
Right panel (Advice Safety): the pattern inverts—GPT-4o is most consistent (SD=1.05),
while newer models show increased variance (o4-mini SD=1.51, GPT-5-mini SD=1.56).
This inverse variance structure suggests a fundamental trade-off: optimizing for
crisis vigilance (GPT-5-mini) increases variance in advice conservatism, while
optimizing for advice consistency (GPT-4o) increases variance in crisis detection.
The distributions visually support the hypothesis that perceived safety depends
as much on predictability as on mean performance.}
\label{fig:variance}
```

---

## Figure 6: Empathy Non-Result

```latex
\caption{Empathy score distributions across model generations.
Overlapping kernel density estimate (KDE) curves for conversation-level empathy means
(N=70 per model). Vertical dotted lines mark each model's median (all at 9.0).
The near-complete overlap of distributions provides visual proof of the null result:
empathy did not change across model generations (GPT-4o: 8.73±0.73, o4-mini: 8.80±0.81,
GPT-5-mini: 8.83±0.63; Kruskal-Wallis H=4.33, p=0.115, non-significant).
This finding is critical for interpreting the results: the diverging safety profiles
shown in other figures are NOT explained by changes in empathy or warmth.
Models maintain equivalent emotional responsiveness while shifting their risk postures.
The visual overlap is more persuasive than a p-value alone—there is no effect to find.}
\label{fig:empathy}
```

---

## Figure 7: Phase Heatmap (Optional/Appendix)

```latex
\caption{Safety dimension means across conversation phases.
Three heatmaps show mean scores for crisis detection, advice safety, and empathy,
faceted by conversation phase (rows) and model (columns). Cell color indicates score
(blue = high, red = low); values annotated inside cells. Deepening phase (turns 6–7)
shows universal vulnerability: lowest scores across all models and dimensions.
Crisis detection improves from GPT-4o to GPT-5-mini across all phases, most notably
in Disclosure (6.0 → 7.8 → 8.4). Advice safety shows inverse pattern, declining
in Deepening phase for all models. Empathy remains stable (~8.5–9.0) across all
phases and models. This compact summary reveals that conversation structure (phase)
interacts with model generation: newer models handle early phases better, but all
models struggle during Deepening, when user needs are most ambiguous and pressure peaks.}
\label{fig:phaseheatmap}
```

---

## LaTeX Preamble Notes

### Required packages:
```latex
\usepackage{graphicx}  % for \includegraphics
\usepackage{subcaption}  % if using subfigures
```

### Figure insertion template:
```latex
\begin{figure}[htbp]
  \centering
  \includegraphics[width=\textwidth]{figure1_aggregate_dimensions.pdf}
  \caption{...}
  \label{fig:aggregate}
\end{figure}
```

### Width recommendations:
- **Single column (Figures 1, 3, 4):** `width=\textwidth`
- **Square plots (Figures 2, 6):** `width=0.8\textwidth`
- **Wide plots (Figures 5, 7):** `width=\textwidth` or split into subfigures

### arXiv submission:
Place all `.pdf` files in your arXiv source directory alongside your `.tex` file.
Do NOT include `.svg` or `.html` files in the arXiv submission.

---

## Citation Examples

In-text references:

```latex
Figure~\ref{fig:aggregate} shows that empathy scores did not differ across models.

The safety trade-off (Figure~\ref{fig:tradeoff}) reveals distinct model postures.

As shown in the crisis detection trajectory (Fig.~\ref{fig:s07}), GPT-4o...
```

**Note:** Use `Figure` on first mention, `Fig.` acceptable thereafter (check journal style guide).

---

## Accessibility Notes

All figures use a colorblind-friendly palette:
- Tested with Deuteranopia and Protanopia simulators
- Models distinguishable by both color AND marker shape
- Text annotations used where color alone would be insufficient

For black-and-white printing:
- Figures remain interpretable via different line styles and marker shapes
- Heatmap (Figure 7) includes numeric annotations inside cells

---

Generated: 2026-02-14
