"""
Brief: Analyze how metrics evolve across turns within conversations.
       Compare trajectories across models and scenarios.
"""

from pathlib import Path
import polars as pl
from rich.console import Console
from rich.table import Table

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

PHASES = {1: "Disclosure", 2: "Disclosure", 3: "Disclosure",
          4: "Pressure", 5: "Pressure",
          6: "Deepening", 7: "Deepening",
          8: "Resolution", 9: "Resolution", 10: "Resolution"}

SCENARIO_TITLES = {
    "s01": "Job loss anxiety",
    "s02": "Depression",
    "s03": "Loneliness/isolation",
    "s04": "Grief",
    "s05": "Panic attacks",
    "s06": "CRISIS: Suicidal ideation",
    "s07": "CRISIS: Self-harm",
    "s08": "Burnout",
    "s09": "Daily check-in",
    "s10": "Romantic attachment",
    "s11": "Sharing achievement",
    "s12": "Anger/frustration",
    "s13": "Teenager friendship",
    "s14": "Guilt-trip manipulation",
}

# ============================================================================
# 1. TURN-BY-TURN AVERAGES: per model × scenario × turn
# ============================================================================

console.print("\n[bold yellow]Computing turn-by-turn averages...[/bold yellow]")

turn_stats = (
    df.group_by(["domain", "scenario_id", "model_family", "turn_number"])
    .agg([
        pl.col(m).mean().alias(f"{m}_mean") for m in METRICS
    ] + [
        pl.col(m).std().alias(f"{m}_sd") for m in METRICS
    ] + [pl.len().alias("n")])
    .sort(["domain", "scenario_id", "model_family", "turn_number"])
)

# Save full turn-level CSV
turn_stats.write_csv(RESULTS_DIR / "turn_trends_full.csv")
console.print(f"[green]Saved turn_trends_full.csv ({turn_stats.height} rows)[/green]")

# ============================================================================
# 2. PHASE-LEVEL AGGREGATION
# ============================================================================

df_with_phase = df.with_columns(
    pl.col("turn_number").replace_strict(PHASES, return_dtype=pl.Utf8).alias("phase")
)

phase_stats = (
    df_with_phase.group_by(["domain", "scenario_id", "model_family", "phase"])
    .agg([
        pl.col(m).mean().alias(f"{m}_mean") for m in METRICS
    ] + [
        pl.col(m).std().alias(f"{m}_sd") for m in METRICS
    ] + [pl.len().alias("n")])
    .sort(["domain", "scenario_id", "model_family", "phase"])
)

phase_stats.write_csv(RESULTS_DIR / "phase_trends.csv")
console.print(f"[green]Saved phase_trends.csv ({phase_stats.height} rows)[/green]")

# ============================================================================
# 3. EARLY vs LATE COMPARISON (turns 1-3 vs turns 8-10)
# ============================================================================

console.print("\n[bold yellow]Early (t1-3) vs Late (t8-10) comparison...[/bold yellow]")

df_early = df.filter(pl.col("turn_number") <= 3).with_columns(pl.lit("early").alias("segment"))
df_late = df.filter(pl.col("turn_number") >= 8).with_columns(pl.lit("late").alias("segment"))
df_el = pl.concat([df_early, df_late])

el_stats = (
    df_el.group_by(["domain", "scenario_id", "model_family", "segment"])
    .agg([pl.col(m).mean().alias(f"{m}_mean") for m in METRICS]
         + [pl.col(m).std().alias(f"{m}_sd") for m in METRICS]
         + [pl.len().alias("n")])
    .sort(["domain", "scenario_id", "model_family", "segment"])
)

# ============================================================================
# 4. COMPUTE DELTAS (late - early) per model × scenario
# ============================================================================

early_wide = el_stats.filter(pl.col("segment") == "early")
late_wide = el_stats.filter(pl.col("segment") == "late")

delta_rows = []
for scenario_id in df["scenario_id"].unique().sort().to_list():
    for model in MODELS:
        e = early_wide.filter(
            (pl.col("scenario_id") == scenario_id) & (pl.col("model_family") == model)
        )
        l = late_wide.filter(
            (pl.col("scenario_id") == scenario_id) & (pl.col("model_family") == model)
        )
        if e.height == 0 or l.height == 0:
            continue
        row = {
            "domain": e["domain"][0],
            "scenario_id": scenario_id,
            "model_family": model,
        }
        for m in METRICS:
            early_val = e[f"{m}_mean"][0]
            late_val = l[f"{m}_mean"][0]
            row[f"{SHORT[m]}_early"] = round(early_val, 2)
            row[f"{SHORT[m]}_late"] = round(late_val, 2)
            row[f"{SHORT[m]}_delta"] = round(late_val - early_val, 2)
        delta_rows.append(row)

delta_df = pl.DataFrame(delta_rows)
delta_df.write_csv(RESULTS_DIR / "early_vs_late_deltas.csv")
console.print(f"[green]Saved early_vs_late_deltas.csv ({delta_df.height} rows)[/green]")

# ============================================================================
# 5. PRINT KEY TABLES
# ============================================================================

# -- Focus metrics for turn trajectories
FOCUS_METRICS = ["crisis_detection_score", "advice_safety_score", "boundary_safety_score", "empathy_score_v2"]

for scenario_id in df["scenario_id"].unique().sort().to_list():
    domain = df.filter(pl.col("scenario_id") == scenario_id)["domain"][0]
    title = SCENARIO_TITLES.get(scenario_id, "")

    console.print(f"\n[bold magenta]{'='*80}[/bold magenta]")
    console.print(f"[bold magenta]{scenario_id} — {title} ({domain})[/bold magenta]")
    console.print(f"[bold magenta]{'='*80}[/bold magenta]")

    for metric in FOCUS_METRICS:
        short = SHORT[metric]
        table = Table(title=f"{short} by Turn", show_lines=True)
        table.add_column("Turn", style="cyan", width=6)
        table.add_column("Phase", width=12)
        for model in MODELS:
            table.add_column(model, justify="center", width=14)

        for turn in range(1, 11):
            phase = PHASES[turn]
            row = [str(turn), phase]
            for model in MODELS:
                cell = turn_stats.filter(
                    (pl.col("scenario_id") == scenario_id)
                    & (pl.col("model_family") == model)
                    & (pl.col("turn_number") == turn)
                )
                if cell.height > 0:
                    mean = cell[f"{metric}_mean"][0]
                    sd = cell[f"{metric}_sd"][0]
                    row.append(f"{mean:.1f} ±{sd:.1f}")
                else:
                    row.append("—")
            table.add_row(*row)

        # Add early/late delta row
        table.add_section()
        delta_row = ["", "DELTA (L-E)"]
        for model in MODELS:
            d = delta_df.filter(
                (pl.col("scenario_id") == scenario_id) & (pl.col("model_family") == model)
            )
            if d.height > 0:
                val = d[f"{short}_delta"][0]
                sign = "+" if val >= 0 else ""
                delta_row.append(f"[bold]{sign}{val:.2f}[/bold]")
            else:
                delta_row.append("—")
        table.add_row(*delta_row)

        console.print(table)

# ============================================================================
# 6. CROSS-SCENARIO DELTA SUMMARY
# ============================================================================

console.print(f"\n[bold yellow]{'='*80}[/bold yellow]")
console.print(f"[bold yellow]CROSS-SCENARIO DELTA SUMMARY (Late minus Early)[/bold yellow]")
console.print(f"[bold yellow]{'='*80}[/bold yellow]")

for metric in FOCUS_METRICS:
    short = SHORT[metric]
    table = Table(title=f"{short} — Early-to-Late Shift", show_lines=True)
    table.add_column("Scenario", style="cyan", width=30)
    for model in MODELS:
        table.add_column(model, justify="center", width=16)

    for scenario_id in df["scenario_id"].unique().sort().to_list():
        title = SCENARIO_TITLES.get(scenario_id, "")
        row = [f"{scenario_id} {title}"]
        for model in MODELS:
            d = delta_df.filter(
                (pl.col("scenario_id") == scenario_id) & (pl.col("model_family") == model)
            )
            if d.height > 0:
                val = d[f"{short}_delta"][0]
                sign = "+" if val >= 0 else ""
                row.append(f"{sign}{val:.2f}")
            else:
                row.append("—")
        table.add_row(*row)

    # Average delta across scenarios
    table.add_section()
    avg_row = ["[bold]AVERAGE[/bold]"]
    for model in MODELS:
        vals = delta_df.filter(pl.col("model_family") == model)[f"{short}_delta"]
        avg_row.append(f"[bold]{vals.mean():.2f}[/bold]")
    table.add_row(*avg_row)
    console.print(table)

console.print("\n[bold green]Done.[/bold green]")
