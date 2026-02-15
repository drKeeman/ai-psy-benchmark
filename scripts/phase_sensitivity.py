"""
Brief: Sensitivity analysis — compare full dataset vs excluding Resolution phase (turns 8-10).
       Shows how much the Resolution phase inflates/masks model differences.
"""

from pathlib import Path
import polars as pl
from rich.console import Console
from rich.table import Table

console = Console()
PROJECT_DIR = Path(__file__).parent.parent
RESULTS_DIR = PROJECT_DIR / "results"

df = pl.read_csv(RESULTS_DIR / "empathyc_analytics_full.csv")

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
SCENARIO_TITLES = {
    "s01": "Job loss anxiety", "s02": "Depression", "s03": "Loneliness/isolation",
    "s04": "Grief", "s05": "Panic attacks", "s06": "CRISIS: Suicidal ideation",
    "s07": "CRISIS: Self-harm", "s08": "Burnout", "s09": "Daily check-in",
    "s10": "Romantic attachment", "s11": "Sharing achievement",
    "s12": "Anger/frustration", "s13": "Teenager friendship",
    "s14": "Guilt-trip manipulation",
}

df_full = df
df_no_res = df.filter(pl.col("turn_number") <= 7)  # turns 1-7 only
df_pressure = df.filter(pl.col("turn_number").is_between(4, 7))  # turns 4-7 (Pressure + Deepening)
df_deep = df.filter(pl.col("turn_number").is_between(6, 7))  # turns 6-7 only (Deepening)

SLICES = {
    "Full (t1-10)": df_full,
    "No Resolution (t1-7)": df_no_res,
    "Pressure+Deep (t4-7)": df_pressure,
    "Deepening only (t6-7)": df_deep,
}

# ============================================================================
# 1. OVERALL BY MODEL — ALL SLICES SIDE BY SIDE
# ============================================================================

console.print("[bold yellow]═══ MODEL COMPARISON ACROSS PHASE SLICES ═══[/bold yellow]\n")

for metric in METRICS:
    short = SHORT[metric]
    table = Table(title=f"{short}", show_lines=True)
    table.add_column("Slice", style="cyan", width=24)
    for model in MODELS:
        table.add_column(f"{model}\nmean±sd", justify="center", width=18)
    table.add_column("Spread\n(max-min)", justify="center", width=10)

    for slice_name, sdf in SLICES.items():
        row = [slice_name]
        means = []
        for model in MODELS:
            col = sdf.filter(pl.col("model_family") == model)[metric].drop_nulls()
            m, s = col.mean(), col.std()
            means.append(m)
            row.append(f"{m:.2f} ±{s:.2f}")
        spread = max(means) - min(means)
        row.append(f"{spread:.2f}")
        table.add_row(*row)
    console.print(table)

# ============================================================================
# 2. BY DOMAIN × MODEL — NO RESOLUTION vs FULL
# ============================================================================

console.print("\n[bold yellow]═══ DOMAIN LEVEL: FULL vs NO-RESOLUTION ═══[/bold yellow]")

for domain in ["mental_health", "companion"]:
    console.print(f"\n[bold magenta]── {domain.upper()} ──[/bold magenta]")

    table = Table(show_lines=True)
    table.add_column("Metric", style="cyan", width=14)
    table.add_column("Slice", width=12)
    for model in MODELS:
        table.add_column(model, justify="center", width=16)
    table.add_column("Spread", justify="center", width=8)

    for metric in METRICS:
        short = SHORT[metric]
        for slice_name, sdf in [("Full", df_full), ("t1-7", df_no_res), ("t4-7", df_pressure)]:
            row = [short if slice_name == "Full" else "", slice_name]
            means = []
            for model in MODELS:
                col = sdf.filter(
                    (pl.col("model_family") == model) & (pl.col("domain") == domain)
                )[metric].drop_nulls()
                m = col.mean()
                means.append(m)
                row.append(f"{m:.2f} ±{col.std():.2f}")
            row.append(f"{max(means) - min(means):.2f}")
            table.add_row(*row)
        table.add_section()
    console.print(table)

# ============================================================================
# 3. SCENARIO-LEVEL: CRISIS SCENARIOS DEEPENING ONLY
# ============================================================================

console.print("\n[bold yellow]═══ CRISIS SCENARIOS — DEEPENING PHASE ONLY (t6-7) ═══[/bold yellow]")

crisis_scenarios = ["s02", "s03", "s06", "s07"]
focus_metrics = ["crisis_detection_score", "advice_safety_score", "empathy_score_v2"]

for sid in crisis_scenarios:
    title = SCENARIO_TITLES[sid]
    table = Table(title=f"{sid} — {title} (Deepening only, t6-7)", show_lines=True)
    table.add_column("Metric", style="cyan", width=14)
    for model in MODELS:
        n = df_deep.filter((pl.col("scenario_id") == sid) & (pl.col("model_family") == model)).height
        table.add_column(f"{model} (n={n})", justify="center", width=18)
    table.add_column("Spread", justify="center", width=8)

    for metric in focus_metrics:
        row = [SHORT[metric]]
        means = []
        for model in MODELS:
            col = df_deep.filter(
                (pl.col("scenario_id") == sid) & (pl.col("model_family") == model)
            )[metric].drop_nulls()
            if len(col) > 0:
                m, s = col.mean(), col.std()
                means.append(m)
                row.append(f"{m:.2f} ±{s:.2f}")
            else:
                means.append(0)
                row.append("—")
        row.append(f"{max(means) - min(means):.2f}")
        table.add_row(*row)
    console.print(table)

# ============================================================================
# 4. ALL SCENARIOS — CRISIS DETECTION SPREAD COMPARISON
# ============================================================================

console.print("\n[bold yellow]═══ CRISIS DETECTION: HOW MUCH DOES SLICE MATTER? ═══[/bold yellow]")

table = Table(title="Crisis Detection — Model Spread by Scenario × Slice", show_lines=True)
table.add_column("Scenario", style="cyan", width=28)
table.add_column("Full\nspread", justify="center", width=10)
table.add_column("t1-7\nspread", justify="center", width=10)
table.add_column("t4-7\nspread", justify="center", width=10)
table.add_column("t6-7\nspread", justify="center", width=10)
table.add_column("Amplification\n(t4-7 / Full)", justify="center", width=14)

for sid in sorted(df["scenario_id"].unique().to_list()):
    title = SCENARIO_TITLES.get(sid, "")
    row = [f"{sid} {title}"]
    spreads = []
    for sdf in [df_full, df_no_res, df_pressure, df_deep]:
        means = []
        for model in MODELS:
            col = sdf.filter(
                (pl.col("scenario_id") == sid) & (pl.col("model_family") == model)
            )["crisis_detection_score"].drop_nulls()
            means.append(col.mean() if len(col) > 0 else 0)
        spread = max(means) - min(means)
        spreads.append(spread)
        row.append(f"{spread:.2f}")

    amp = spreads[2] / spreads[0] if spreads[0] > 0.01 else 0
    row.append(f"{amp:.1f}x")
    table.add_row(*row)

# Averages
table.add_section()
avg_row = ["[bold]AVERAGE[/bold]"]
for sdf in [df_full, df_no_res, df_pressure, df_deep]:
    all_spreads = []
    for sid in sorted(df["scenario_id"].unique().to_list()):
        means = []
        for model in MODELS:
            col = sdf.filter(
                (pl.col("scenario_id") == sid) & (pl.col("model_family") == model)
            )["crisis_detection_score"].drop_nulls()
            means.append(col.mean() if len(col) > 0 else 0)
        all_spreads.append(max(means) - min(means))
    avg_row.append(f"{sum(all_spreads)/len(all_spreads):.2f}")
avg_row.append("")
table.add_row(*avg_row)

console.print(table)

# ============================================================================
# 5. SAME FOR ADVICE SAFETY
# ============================================================================

console.print("\n[bold yellow]═══ ADVICE SAFETY: HOW MUCH DOES SLICE MATTER? ═══[/bold yellow]")

table = Table(title="Advice Safety — Model Spread by Scenario × Slice", show_lines=True)
table.add_column("Scenario", style="cyan", width=28)
table.add_column("Full\nspread", justify="center", width=10)
table.add_column("t1-7\nspread", justify="center", width=10)
table.add_column("t4-7\nspread", justify="center", width=10)
table.add_column("t6-7\nspread", justify="center", width=10)

for sid in sorted(df["scenario_id"].unique().to_list()):
    title = SCENARIO_TITLES.get(sid, "")
    row = [f"{sid} {title}"]
    for sdf in [df_full, df_no_res, df_pressure, df_deep]:
        means = []
        for model in MODELS:
            col = sdf.filter(
                (pl.col("scenario_id") == sid) & (pl.col("model_family") == model)
            )["advice_safety_score"].drop_nulls()
            means.append(col.mean() if len(col) > 0 else 0)
        row.append(f"{max(means) - min(means):.2f}")
    table.add_row(*row)

table.add_section()
avg_row = ["[bold]AVERAGE[/bold]"]
for sdf in [df_full, df_no_res, df_pressure, df_deep]:
    all_spreads = []
    for sid in sorted(df["scenario_id"].unique().to_list()):
        means = []
        for model in MODELS:
            col = sdf.filter(
                (pl.col("scenario_id") == sid) & (pl.col("model_family") == model)
            )["advice_safety_score"].drop_nulls()
            means.append(col.mean() if len(col) > 0 else 0)
        all_spreads.append(max(means) - min(means))
    avg_row.append(f"{sum(all_spreads)/len(all_spreads):.2f}")
table.add_row(*avg_row)

console.print(table)

console.print("\n[bold green]Done.[/bold green]")
