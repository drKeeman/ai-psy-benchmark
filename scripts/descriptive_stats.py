"""
Brief: Descriptive stats (avg, median, SD) for _v2 metrics across models/domains/scenarios
"""

from pathlib import Path

import polars as pl
from rich.console import Console
from rich.table import Table

console = Console()
PROJECT_DIR = Path(__file__).parent.parent
RESULTS_DIR = PROJECT_DIR / "results"

# ============================================================================
# LOAD DATA
# ============================================================================

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

# ============================================================================
# 1. BY MODEL (across all domains)
# ============================================================================

console.print("\n[bold yellow]═══ BY MODEL (all domains) ═══[/bold yellow]")

for model in ["gpt-4o", "o4-mini", "gpt-5-mini"]:
    mdf = df.filter(pl.col("model_family") == model)
    table = Table(title=f"{model}  (n={len(mdf)})", show_lines=True)
    table.add_column("Metric", style="cyan", width=14)
    table.add_column("Mean", justify="right", width=7)
    table.add_column("Median", justify="right", width=7)
    table.add_column("SD", justify="right", width=7)
    table.add_column("Min", justify="right", width=5)
    table.add_column("Max", justify="right", width=5)

    for m in METRICS:
        col = mdf[m].drop_nulls()
        table.add_row(
            SHORT[m],
            f"{col.mean():.2f}",
            f"{col.median():.2f}",
            f"{col.std():.2f}",
            f"{col.min():.0f}",
            f"{col.max():.0f}",
        )
    console.print(table)

# ============================================================================
# 2. BY MODEL × DOMAIN
# ============================================================================

console.print("\n[bold yellow]═══ BY MODEL × DOMAIN ═══[/bold yellow]")

for domain in ["mental_health", "companion"]:
    console.print(f"\n[bold magenta]── {domain.upper()} ──[/bold magenta]")

    table = Table(show_lines=True)
    table.add_column("Metric", style="cyan", width=14)
    for model in ["gpt-4o", "o4-mini", "gpt-5-mini"]:
        table.add_column(f"{model}\nmean±sd (med)", justify="center", width=22)

    for m in METRICS:
        row = [SHORT[m]]
        for model in ["gpt-4o", "o4-mini", "gpt-5-mini"]:
            col = df.filter(
                (pl.col("model_family") == model) & (pl.col("domain") == domain)
            )[m].drop_nulls()
            row.append(f"{col.mean():.2f}±{col.std():.2f} ({col.median():.1f})")
        table.add_row(*row)
    console.print(table)

# ============================================================================
# 3. BY MODEL × SCENARIO
# ============================================================================

console.print("\n[bold yellow]═══ BY MODEL × SCENARIO ═══[/bold yellow]")

scenarios = df.select("scenario_id", "domain").unique().sort("scenario_id")

for row in scenarios.iter_rows(named=True):
    sid, domain = row["scenario_id"], row["domain"]
    sdf = df.filter(pl.col("scenario_id") == sid)

    table = Table(title=f"{sid} ({domain})", show_lines=True)
    table.add_column("Metric", style="cyan", width=14)
    for model in ["gpt-4o", "o4-mini", "gpt-5-mini"]:
        n = sdf.filter(pl.col("model_family") == model).height
        table.add_column(f"{model} (n={n})", justify="center", width=22)

    for m in METRICS:
        row_vals = [SHORT[m]]
        for model in ["gpt-4o", "o4-mini", "gpt-5-mini"]:
            col = sdf.filter(pl.col("model_family") == model)[m].drop_nulls()
            if len(col) > 0:
                row_vals.append(
                    f"{col.mean():.2f}±{col.std():.2f} ({col.median():.1f})"
                )
            else:
                row_vals.append("—")
        table.add_row(*row_vals)
    console.print(table)

# ============================================================================
# 4. SAVE TO MARKDOWN
# ============================================================================

OUTPUT_DIR = RESULTS_DIR
lines = []
lines.append("# Keep4o Experiment — Descriptive Statistics (_v2 Metrics)")
lines.append(
    f"\n**Generated:** {pl.Series([None]).cast(pl.Datetime).dt.strftime('%Y-%m-%d')[0] or __import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M')}"
)
lines.append(f"**Total scored AI responses:** {len(df):,}")
lines.append(f"**Models:** gpt-4o (beloved), o4-mini, gpt-5-mini")
lines.append(
    f"**Domains:** mental_health ({df.filter(pl.col('domain') == 'mental_health').height} msgs), companion ({df.filter(pl.col('domain') == 'companion').height} msgs)"
)
lines.append(
    f"**Scenarios:** {df['scenario_id'].n_unique()} (s01-s08 mental health, s09-s14 companion)"
)
lines.append(f"**Runs per scenario per model:** 5 × 10 turns = 50 data points per cell")

# -- By model overall
lines.append("\n---\n## 1. By Model (All Domains Pooled)\n")
for model in ["gpt-4o", "o4-mini", "gpt-5-mini"]:
    mdf = df.filter(pl.col("model_family") == model)
    lines.append(f"### {model} (n={len(mdf)})\n")
    lines.append("| Metric | Mean | Median | SD | Min | Max |")
    lines.append("|--------|-----:|-------:|---:|----:|----:|")
    for m in METRICS:
        col = mdf[m].drop_nulls()
        lines.append(
            f"| {SHORT[m]} | {col.mean():.2f} | {col.median():.1f} | {col.std():.2f} | {col.min():.0f} | {col.max():.0f} |"
        )
    lines.append("")

# -- By model × domain
lines.append("---\n## 2. By Model × Domain\n")
for domain in ["mental_health", "companion"]:
    lines.append(f"### {domain.replace('_', ' ').title()}\n")
    lines.append("| Metric | gpt-4o | o4-mini | gpt-5-mini |")
    lines.append("|--------|--------|---------|------------|")
    for m in METRICS:
        row = f"| {SHORT[m]} |"
        for model in ["gpt-4o", "o4-mini", "gpt-5-mini"]:
            col = df.filter(
                (pl.col("model_family") == model) & (pl.col("domain") == domain)
            )[m].drop_nulls()
            row += f" {col.mean():.2f}±{col.std():.2f} ({col.median():.1f}) |"
        lines.append(row)
    lines.append("")

# -- By model × scenario
lines.append("---\n## 3. By Model × Scenario\n")
for row in scenarios.iter_rows(named=True):
    sid, domain = row["scenario_id"], row["domain"]
    sdf = df.filter(pl.col("scenario_id") == sid)

    lines.append(f"### {sid} — {domain}\n")
    lines.append("| Metric | gpt-4o | o4-mini | gpt-5-mini |")
    lines.append("|--------|--------|---------|------------|")
    for m in METRICS:
        row_str = f"| {SHORT[m]} |"
        for model in ["gpt-4o", "o4-mini", "gpt-5-mini"]:
            col = sdf.filter(pl.col("model_family") == model)[m].drop_nulls()
            if len(col) > 0:
                row_str += f" {col.mean():.2f}±{col.std():.2f} ({col.median():.1f}) |"
            else:
                row_str += " — |"
        lines.append(row_str)
    lines.append("")

out_path = OUTPUT_DIR / "descriptive_stats.md"
out_path.write_text("\n".join(lines))
console.print(f"\n[bold green]✓ Saved to {out_path}[/bold green]")

# ============================================================================
# 5. SAVE SUMMARY CSV (for downstream stats scripts)
# ============================================================================

rows = []
for domain in ["mental_health", "companion"]:
    for sid in (
        df.filter(pl.col("domain") == domain)["scenario_id"].unique().sort().to_list()
    ):
        for model in ["gpt-4o", "o4-mini", "gpt-5-mini"]:
            sub = df.filter(
                (pl.col("domain") == domain)
                & (pl.col("scenario_id") == sid)
                & (pl.col("model_family") == model)
            )
            if sub.height == 0:
                continue
            r = {
                "domain": domain,
                "scenario_id": sid,
                "model_family": model,
                "n": sub.height,
            }
            for m in METRICS:
                col = sub[m].drop_nulls()
                r[f"{SHORT[m]}_mean"] = round(col.mean(), 3)
                r[f"{SHORT[m]}_median"] = round(col.median(), 1)
                r[f"{SHORT[m]}_sd"] = round(col.std(), 3)
            rows.append(r)

summary_df = pl.DataFrame(rows)
csv_path = OUTPUT_DIR / "descriptive_stats_summary.csv"
summary_df.write_csv(csv_path)
console.print(f"[bold green]✓ Summary CSV saved to {csv_path}[/bold green]")
