"""
Brief: Formal statistical tests (Kruskal-Wallis, Mann-Whitney U, Levene's, effect sizes)
Tests run on both full dataset and Pressure+Deepening slice.
"""

from pathlib import Path

import numpy as np
import polars as pl
from rich.console import Console
from rich.table import Table
from scipy import stats

console = Console()
PROJECT_DIR = Path(__file__).parent.parent
RESULTS_DIR = PROJECT_DIR / "results"

df = pl.read_csv(RESULTS_DIR / "empathyc_analytics_full.csv")
console.print(f"[bold cyan]Loaded {len(df):,} rows[/bold cyan]")

METRICS = [
    "empathy_score_v2",
    "reliability_score_v2",
    "consistency_score_v2",
    "crisis_detection_score",
    "advice_safety_score",
    "boundary_safety_score",
    "ai_trust_score",
]
SHORT = {
    "empathy_score_v2": "Empathy",
    "reliability_score_v2": "Reliability",
    "consistency_score_v2": "Consistency",
    "crisis_detection_score": "Crisis Det.",
    "advice_safety_score": "Advice Safety",
    "boundary_safety_score": "Boundary",
    "ai_trust_score": "Trust",
}
MODELS = ["gpt-4o", "o4-mini", "gpt-5-mini"]
PAIRS = [("gpt-4o", "o4-mini"), ("gpt-4o", "gpt-5-mini"), ("o4-mini", "gpt-5-mini")]

SCENARIO_TITLES = {
    "s01": "Job loss anxiety",
    "s02": "Depression",
    "s03": "Loneliness",
    "s04": "Grief",
    "s05": "Panic attacks",
    "s06": "CRISIS: Suicidal ideation",
    "s07": "CRISIS: Self-harm",
    "s08": "Burnout",
    "s09": "Daily check-in",
    "s10": "Romantic attachment",
    "s11": "Achievement",
    "s12": "Anger",
    "s13": "Teen friendship",
    "s14": "Manipulation",
}


def sig_stars(p):
    if p < 0.001:
        return "***"
    if p < 0.01:
        return "**"
    if p < 0.05:
        return "*"
    return "ns"


def cliffs_delta(x, y):
    """Cliff's delta effect size (non-parametric)."""
    nx, ny = len(x), len(y)
    if nx == 0 or ny == 0:
        return 0.0
    more = sum(1 for xi in x for yi in y if xi > yi)
    less = sum(1 for xi in x for yi in y if xi < yi)
    return (more - less) / (nx * ny)


def cliffs_label(d):
    d = abs(d)
    if d < 0.147:
        return "negligible"
    if d < 0.33:
        return "small"
    if d < 0.474:
        return "medium"
    return "large"


def get_conv_means(data, metric):
    """Aggregate to conversation-level means to avoid pseudoreplication."""
    return data.group_by(["model_family", "conv_id"]).agg(
        pl.col(metric).mean().alias("value")
    )


def run_tests(data, metric, label=""):
    """Run Kruskal-Wallis + pairwise Mann-Whitney + Levene's for one metric on one slice."""
    groups = {}
    for model in MODELS:
        vals = data.filter(pl.col("model_family") == model)["value"].to_numpy()
        groups[model] = vals

    # Kruskal-Wallis (3-group comparison)
    kw_stat, kw_p = stats.kruskal(*groups.values())

    # Pairwise Mann-Whitney U with Bonferroni correction
    pairwise = {}
    for a, b in PAIRS:
        u_stat, u_p = stats.mannwhitneyu(groups[a], groups[b], alternative="two-sided")
        p_corr = min(u_p * 3, 1.0)  # Bonferroni for 3 comparisons
        cd = cliffs_delta(groups[a].tolist(), groups[b].tolist())
        pairwise[(a, b)] = {"U": u_stat, "p": u_p, "p_corr": p_corr, "cliff_d": cd}

    # Levene's test for equal variances
    lev_stat, lev_p = stats.levene(*groups.values())

    return {
        "kw_stat": kw_stat,
        "kw_p": kw_p,
        "pairwise": pairwise,
        "lev_stat": lev_stat,
        "lev_p": lev_p,
        "means": {m: np.mean(v) for m, v in groups.items()},
        "sds": {m: np.std(v, ddof=1) for m, v in groups.items()},
        "ns": {m: len(v) for m, v in groups.items()},
    }


# ============================================================================
# Prepare slices
# ============================================================================

slices = {
    "Full (t1-10)": df,
    "Pressure+Deep (t4-7)": df.filter(pl.col("turn_number").is_between(4, 7)),
}

lines = []  # for markdown output
lines.append("# Keep4o Experiment — Formal Statistical Tests")
lines.append(
    f"\n**Generated:** {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M')}"
)
lines.append(
    "**Tests:** Kruskal-Wallis (3-group), Mann-Whitney U (pairwise, Bonferroni-corrected), Levene's (variance equality)"
)
lines.append(
    "**Effect size:** Cliff's delta (negligible < 0.147 < small < 0.33 < medium < 0.474 < large)"
)
lines.append(
    "**Aggregation:** Conversation-level means (avg across turns per conversation) to avoid pseudoreplication"
)
lines.append(f"**Alpha:** 0.05 (Bonferroni-corrected for pairwise: 0.05/3 = 0.0167)")

# ============================================================================
# 1. OVERALL BY DOMAIN × METRIC
# ============================================================================

for slice_name, slice_df in slices.items():
    console.print(f"\n[bold yellow]{'=' * 80}[/bold yellow]")
    console.print(f"[bold yellow]{slice_name}[/bold yellow]")
    console.print(f"[bold yellow]{'=' * 80}[/bold yellow]")

    lines.append(f"\n---\n## {slice_name}\n")

    for domain in ["mental_health", "companion", None]:
        domain_label = domain.replace("_", " ").title() if domain else "All Domains"
        ddf = slice_df.filter(pl.col("domain") == domain) if domain else slice_df

        console.print(f"\n[bold magenta]── {domain_label} ──[/bold magenta]")
        lines.append(f"\n### {domain_label}\n")

        # Kruskal-Wallis summary table
        table = Table(
            title=f"Kruskal-Wallis + Levene's — {domain_label}", show_lines=True
        )
        table.add_column("Metric", style="cyan", width=14)
        table.add_column("KW H", justify="right", width=8)
        table.add_column("KW p", justify="right", width=10)
        table.add_column("Sig", width=5)
        table.add_column("Levene F", justify="right", width=9)
        table.add_column("Lev p", justify="right", width=10)
        table.add_column("Var Sig", width=5)

        lines.append("#### Omnibus Tests (Kruskal-Wallis + Levene's)\n")
        lines.append("| Metric | KW H | KW p | Sig | Levene F | Lev p | Var Sig |")
        lines.append("|--------|-----:|-----:|-----|--------:|------:|---------|")

        kw_results = {}
        for metric in METRICS:
            conv_data = get_conv_means(ddf, metric)
            r = run_tests(conv_data, metric)
            kw_results[metric] = r

            table.add_row(
                SHORT[metric],
                f"{r['kw_stat']:.2f}",
                f"{r['kw_p']:.4f}" if r["kw_p"] >= 0.0001 else f"{r['kw_p']:.2e}",
                sig_stars(r["kw_p"]),
                f"{r['lev_stat']:.2f}",
                f"{r['lev_p']:.4f}" if r["lev_p"] >= 0.0001 else f"{r['lev_p']:.2e}",
                sig_stars(r["lev_p"]),
            )
            kw_p_str = f"{r['kw_p']:.4f}" if r["kw_p"] >= 0.0001 else f"{r['kw_p']:.2e}"
            lev_p_str = (
                f"{r['lev_p']:.4f}" if r["lev_p"] >= 0.0001 else f"{r['lev_p']:.2e}"
            )
            lines.append(
                f"| {SHORT[metric]} | {r['kw_stat']:.2f} | {kw_p_str} | {sig_stars(r['kw_p'])} | {r['lev_stat']:.2f} | {lev_p_str} | {sig_stars(r['lev_p'])} |"
            )

        console.print(table)
        lines.append("")

        # Pairwise Mann-Whitney table
        table2 = Table(
            title=f"Pairwise Mann-Whitney U — {domain_label}", show_lines=True
        )
        table2.add_column("Metric", style="cyan", width=14)
        table2.add_column("Comparison", width=20)
        table2.add_column("U", justify="right", width=10)
        table2.add_column("p (raw)", justify="right", width=10)
        table2.add_column("p (Bonf)", justify="right", width=10)
        table2.add_column("Sig", width=5)
        table2.add_column("Cliff's d", justify="right", width=9)
        table2.add_column("Effect", width=12)

        lines.append(
            "#### Pairwise Comparisons (Mann-Whitney U, Bonferroni-corrected)\n"
        )
        lines.append(
            "| Metric | Comparison | U | p (raw) | p (Bonf) | Sig | Cliff's d | Effect |"
        )
        lines.append(
            "|--------|------------|--:|--------:|---------:|-----|----------:|--------|"
        )

        for metric in METRICS:
            r = kw_results[metric]
            for a, b in PAIRS:
                pw = r["pairwise"][(a, b)]
                p_str = f"{pw['p']:.4f}" if pw["p"] >= 0.0001 else f"{pw['p']:.2e}"
                pc_str = (
                    f"{pw['p_corr']:.4f}"
                    if pw["p_corr"] >= 0.0001
                    else f"{pw['p_corr']:.2e}"
                )
                table2.add_row(
                    SHORT[metric],
                    f"{a} vs {b}",
                    f"{pw['U']:.0f}",
                    p_str,
                    pc_str,
                    sig_stars(pw["p_corr"]),
                    f"{pw['cliff_d']:+.3f}",
                    cliffs_label(pw["cliff_d"]),
                )
                lines.append(
                    f"| {SHORT[metric]} | {a} vs {b} | {pw['U']:.0f} | {p_str} | {pc_str} | {sig_stars(pw['p_corr'])} | {pw['cliff_d']:+.3f} | {cliffs_label(pw['cliff_d'])} |"
                )

        console.print(table2)
        lines.append("")

# ============================================================================
# 2. SCENARIO-LEVEL TESTS (key metrics only)
# ============================================================================

console.print(f"\n[bold yellow]{'=' * 80}[/bold yellow]")
console.print(f"[bold yellow]SCENARIO-LEVEL TESTS (Full dataset)[/bold yellow]")
console.print(f"[bold yellow]{'=' * 80}[/bold yellow]")

lines.append("\n---\n## Scenario-Level Tests (Full Dataset)\n")

focus = ["crisis_detection_score", "advice_safety_score", "empathy_score_v2"]

# Summary: KW p-values per scenario × metric
table3 = Table(
    title="Kruskal-Wallis p-values by Scenario (conversation-level)", show_lines=True
)
table3.add_column("Scenario", style="cyan", width=28)
for m in focus:
    table3.add_column(f"{SHORT[m]}\nKW p", justify="center", width=16)

lines.append("### Kruskal-Wallis p-values (conversation-level means)\n")
lines.append("| Scenario | Crisis Det. p | Advice Safety p | Empathy p |")
lines.append("|----------|--------------|-----------------|-----------|")

for sid in sorted(df["scenario_id"].unique().to_list()):
    sdf = df.filter(pl.col("scenario_id") == sid)
    title = SCENARIO_TITLES.get(sid, "")
    row = [f"{sid} {title}"]
    md_row = f"| {sid} {title} |"

    for metric in focus:
        conv_data = get_conv_means(sdf, metric)
        groups = []
        for model in MODELS:
            vals = conv_data.filter(pl.col("model_family") == model)["value"].to_numpy()
            groups.append(vals)

        if all(len(g) >= 3 for g in groups):
            kw_stat, kw_p = stats.kruskal(*groups)
            p_str = f"{kw_p:.4f}" if kw_p >= 0.0001 else f"{kw_p:.2e}"
            row.append(f"{p_str} {sig_stars(kw_p)}")
            md_row += f" {p_str} {sig_stars(kw_p)} |"
        else:
            row.append("n/a")
            md_row += " n/a |"

    table3.add_row(*row)
    lines.append(md_row)

console.print(table3)
lines.append("")

# ============================================================================
# 3. SCENARIO-LEVEL PAIRWISE FOR SIGNIFICANT RESULTS
# ============================================================================

lines.append("\n### Significant Scenario-Level Pairwise Tests\n")
lines.append(
    "Only showing scenarios where Kruskal-Wallis p < 0.05 for at least one focus metric.\n"
)

for sid in sorted(df["scenario_id"].unique().to_list()):
    sdf = df.filter(pl.col("scenario_id") == sid)
    title = SCENARIO_TITLES.get(sid, "")

    has_sig = False
    scenario_lines = []
    scenario_lines.append(f"\n#### {sid} — {title}\n")
    scenario_lines.append(
        "| Metric | Comparison | U | p (Bonf) | Sig | Cliff's d | Effect |"
    )
    scenario_lines.append(
        "|--------|------------|--:|---------:|-----|----------:|--------|"
    )

    for metric in focus:
        conv_data = get_conv_means(sdf, metric)
        groups = {}
        for model in MODELS:
            groups[model] = conv_data.filter(pl.col("model_family") == model)[
                "value"
            ].to_numpy()

        if any(len(v) < 3 for v in groups.values()):
            continue

        kw_stat, kw_p = stats.kruskal(*groups.values())
        if kw_p >= 0.05:
            continue

        has_sig = True
        for a, b in PAIRS:
            u_stat, u_p = stats.mannwhitneyu(
                groups[a], groups[b], alternative="two-sided"
            )
            p_corr = min(u_p * 3, 1.0)
            cd = cliffs_delta(groups[a].tolist(), groups[b].tolist())
            pc_str = f"{p_corr:.4f}" if p_corr >= 0.0001 else f"{p_corr:.2e}"
            scenario_lines.append(
                f"| {SHORT[metric]} | {a} vs {b} | {u_stat:.0f} | {pc_str} | {sig_stars(p_corr)} | {cd:+.3f} | {cliffs_label(cd)} |"
            )

    if has_sig:
        lines.extend(scenario_lines)
        lines.append("")

# ============================================================================
# 4. VARIANCE TESTS (phase-stratified)
# ============================================================================

console.print(f"\n[bold yellow]{'=' * 80}[/bold yellow]")
console.print(
    f"[bold yellow]VARIANCE TESTS — DEEPENING PHASE ONLY (t6-7)[/bold yellow]"
)
console.print(f"[bold yellow]{'=' * 80}[/bold yellow]")

lines.append("\n---\n## Variance Tests — Deepening Phase (t6-7)\n")
lines.append(
    "Testing whether model generations differ in *consistency* (variance), not just level.\n"
)

df_deep = df.filter(pl.col("turn_number").is_between(6, 7))

table4 = Table(title="Levene's Test — Deepening Phase", show_lines=True)
table4.add_column("Domain", width=14)
table4.add_column("Metric", style="cyan", width=14)
table4.add_column("gpt-4o SD", justify="right", width=9)
table4.add_column("o4-mini SD", justify="right", width=9)
table4.add_column("5-mini SD", justify="right", width=9)
table4.add_column("SD ratio\n(4o/5m)", justify="right", width=9)
table4.add_column("Levene F", justify="right", width=9)
table4.add_column("p", justify="right", width=10)
table4.add_column("Sig", width=5)

lines.append(
    "| Domain | Metric | gpt-4o SD | o4-mini SD | 5-mini SD | SD ratio (4o/5m) | Levene F | p | Sig |"
)
lines.append(
    "|--------|--------|-----------|-----------|-----------|-----------------|--------:|--:|-----|"
)

for domain in ["mental_health", "companion"]:
    for metric in METRICS:
        ddf = df_deep.filter(pl.col("domain") == domain)
        groups = []
        sds = []
        for model in MODELS:
            vals = (
                ddf.filter(pl.col("model_family") == model)[metric]
                .drop_nulls()
                .to_numpy()
            )
            groups.append(vals)
            sds.append(np.std(vals, ddof=1) if len(vals) > 1 else 0)

        if all(len(g) >= 3 for g in groups):
            lev_stat, lev_p = stats.levene(*groups)
            ratio = sds[0] / sds[2] if sds[2] > 0.01 else 0
            p_str = f"{lev_p:.4f}" if lev_p >= 0.0001 else f"{lev_p:.2e}"

            table4.add_row(
                domain.replace("_", " ").title(),
                SHORT[metric],
                f"{sds[0]:.2f}",
                f"{sds[1]:.2f}",
                f"{sds[2]:.2f}",
                f"{ratio:.1f}x",
                f"{lev_stat:.2f}",
                p_str,
                sig_stars(lev_p),
            )
            lines.append(
                f"| {domain.replace('_', ' ').title()} | {SHORT[metric]} | {sds[0]:.2f} | {sds[1]:.2f} | {sds[2]:.2f} | {ratio:.1f}x | {lev_stat:.2f} | {p_str} | {sig_stars(lev_p)} |"
            )

console.print(table4)
lines.append("")

# ============================================================================
# SAVE
# ============================================================================

out_path = RESULTS_DIR / "formal_stats.md"
out_path.write_text("\n".join(lines))
console.print(f"\n[bold green]✓ Saved to {out_path}[/bold green]")
