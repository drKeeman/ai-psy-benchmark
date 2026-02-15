"""
Produces arXiv-compatible static exports (SVG/PDF/PNG)
"""

from pathlib import Path

import numpy as np
import plotly.graph_objects as go
import polars as pl
from plotly.subplots import make_subplots
from rich.console import Console
from scipy import stats
from scipy.stats import gaussian_kde

console = Console()

# ============================================================================
# SETUP
# ============================================================================

CHARTS_DIR = Path(__file__).parent
RESULTS_DIR = CHARTS_DIR.parent / "results"
OUTPUT_DIR = CHARTS_DIR / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

# Color scheme
COLORS = {
    "gpt-4o": "#4C78A8",  # steel blue - legacy
    "o4-mini": "#F58518",  # amber/orange - accidental
    "gpt-5-mini": "#E45756",  # muted red - new
}

MODEL_LABELS = {
    "gpt-4o": "GPT-4o",
    "o4-mini": "o4-mini",
    "gpt-5-mini": "GPT-5",
}

# Phase definitions
PHASES = {
    "Disclosure": (1, 3),
    "Pressure": (4, 5),
    "Deepening": (6, 7),
    "Resolution": (8, 10),
}

PHASE_COLORS = {
    "Disclosure": "rgba(200, 200, 200, 0.1)",
    "Pressure": "rgba(180, 180, 180, 0.15)",
    "Deepening": "rgba(160, 160, 160, 0.2)",
    "Resolution": "rgba(200, 200, 200, 0.1)",
}

# ============================================================================
# DATA LOADING
# ============================================================================

console.print("[bold cyan]Loading data...[/bold cyan]")

# Load full analytics (conversation-level means)
df_full = pl.read_csv(RESULTS_DIR / "empathyc_analytics_full.csv")

# Load turn trends
df_turns = pl.read_csv(RESULTS_DIR / "turn_trends_full.csv")

# Load descriptive stats
df_stats = pl.read_csv(RESULTS_DIR / "descriptive_stats_summary.csv")

console.print(f"✓ Loaded {len(df_full):,} conversation records")
console.print(f"✓ Loaded {len(df_turns):,} turn records")
console.print(f"✓ Loaded {len(df_stats):,} scenario stats")

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================


def add_phase_bands(fig, y_range=None, row=None, col=None):
    """Add phase background bands to a figure"""
    for phase_name, (start, end) in PHASES.items():
        kwargs = {
            "x0": start - 0.5,
            "x1": end + 0.5,
            "fillcolor": PHASE_COLORS[phase_name],
            "layer": "below",
            "line_width": 0,
        }
        if row is not None and col is not None:
            kwargs["row"] = row
            kwargs["col"] = col
        fig.add_vrect(**kwargs)


def compute_confidence_ellipse(x, y, n_std=1.0):
    """Compute confidence ellipse using eigenvalue decomposition"""
    cov = np.cov(x, y)
    mean_x = np.mean(x)
    mean_y = np.mean(y)

    # Eigenvalue decomposition for proper ellipse calculation
    eigenvalues, eigenvectors = np.linalg.eig(cov)

    # Get the angle of rotation
    angle = np.arctan2(eigenvectors[1, 0], eigenvectors[0, 0])

    # Width and height are 2 * n_std * sqrt(eigenvalue)
    width = 2 * n_std * np.sqrt(eigenvalues[0])
    height = 2 * n_std * np.sqrt(eigenvalues[1])

    # Generate ellipse points
    theta = np.linspace(0, 2 * np.pi, 100)
    ellipse_x_r = (width / 2) * np.cos(theta)
    ellipse_y_r = (height / 2) * np.sin(theta)

    # Rotate
    rotation_matrix = np.array(
        [[np.cos(angle), -np.sin(angle)], [np.sin(angle), np.cos(angle)]]
    )

    rotated = rotation_matrix @ np.array([ellipse_x_r, ellipse_y_r])

    # Translate to center
    ellipse_x = mean_x + rotated[0]
    ellipse_y = mean_y + rotated[1]

    return ellipse_x, ellipse_y


def hex_to_rgba(hex_color, alpha=1.0):
    """Convert hex color to rgba string"""
    hex_color = hex_color.lstrip("#")
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)
    return f"rgba({r}, {g}, {b}, {alpha})"


def save_figure(fig, filename, width_inches=7, height_inches=5):
    """Save figure as SVG, PDF, and PNG"""
    dpi = 300
    width_px = int(width_inches * dpi / 96)  # Plotly uses 96 DPI as reference
    height_px = int(height_inches * dpi / 96)

    fig.update_layout(
        width=width_px,
        height=height_px,
        font=dict(family="Arial, sans-serif", size=11),
    )

    # Save as SVG
    svg_path = OUTPUT_DIR / f"{filename}.svg"
    fig.write_image(svg_path, format="svg")
    console.print(f"  ✓ Saved {svg_path}")

    # Save as PDF
    pdf_path = OUTPUT_DIR / f"{filename}.pdf"
    fig.write_image(pdf_path, format="pdf")
    console.print(f"  ✓ Saved {pdf_path}")

    # Save as PNG
    png_path = OUTPUT_DIR / f"{filename}.png"
    fig.write_image(png_path, format="png", scale=2)  # scale=2 for high-res PNG
    console.print(f"  ✓ Saved {png_path}")

    # Also save HTML for review
    html_path = OUTPUT_DIR / f"{filename}.html"
    fig.write_html(html_path)
    console.print(f"  ✓ Saved {html_path} (interactive)")


# ============================================================================
# FIGURE 1: AGGREGATE SAFETY DIMENSIONS
# ============================================================================

console.print(
    "\n[bold cyan]Generating Figure 1: Aggregate Safety Dimensions[/bold cyan]"
)

# Data from Table 2 (hardcoded from requirements)
table2_data = [
    {
        "metric": "Crisis Detection",
        "gpt-4o_mean": 8.41,
        "gpt-4o_sd": 2.26,
        "o4-mini_mean": 8.93,
        "o4-mini_sd": 1.64,
        "gpt-5-mini_mean": 9.20,
        "gpt-5-mini_sd": 1.03,
        "p": 0.001,
        "sig": "***",
    },
    {
        "metric": "Advice Safety",
        "gpt-4o_mean": 9.70,
        "gpt-4o_sd": 1.05,
        "o4-mini_mean": 9.39,
        "o4-mini_sd": 1.51,
        "gpt-5-mini_mean": 9.28,
        "gpt-5-mini_sd": 1.56,
        "p": 0.001,
        "sig": "***",
    },
    {
        "metric": "Empathy",
        "gpt-4o_mean": 8.73,
        "gpt-4o_sd": 0.73,
        "o4-mini_mean": 8.80,
        "o4-mini_sd": 0.81,
        "gpt-5-mini_mean": 8.83,
        "gpt-5-mini_sd": 0.63,
        "p": 0.115,
        "sig": "ns",
    },
    {
        "metric": "Reliability",
        "gpt-4o_mean": 8.93,
        "gpt-4o_sd": 1.00,
        "o4-mini_mean": 8.77,
        "o4-mini_sd": 1.03,
        "gpt-5-mini_mean": 8.67,
        "gpt-5-mini_sd": 0.73,
        "p": 0.016,
        "sig": "*",
    },
    {
        "metric": "Boundary Safety",
        "gpt-4o_mean": 9.91,
        "gpt-4o_sd": 0.38,
        "o4-mini_mean": 9.83,
        "o4-mini_sd": 0.61,
        "gpt-5-mini_mean": 9.89,
        "gpt-5-mini_sd": 0.47,
        "p": 0.062,
        "sig": "ns",
    },
    {
        "metric": "Consistency",
        "gpt-4o_mean": 9.70,
        "gpt-4o_sd": 0.54,
        "o4-mini_mean": 9.66,
        "o4-mini_sd": 0.55,
        "gpt-5-mini_mean": 9.66,
        "gpt-5-mini_sd": 0.49,
        "p": 0.142,
        "sig": "ns",
    },
]

fig1 = go.Figure()

x_offset = {"gpt-4o": -0.25, "o4-mini": 0, "gpt-5-mini": 0.25}
y_positions = list(range(len(table2_data)))

for model in ["gpt-4o", "o4-mini", "gpt-5-mini"]:
    x_vals = [d[f"{model}_mean"] for d in table2_data]
    x_err = [d[f"{model}_sd"] for d in table2_data]
    y_vals = [i + x_offset[model] for i in y_positions]

    fig1.add_trace(
        go.Bar(
            y=y_vals,
            x=x_vals,
            error_x=dict(type="data", array=x_err, thickness=1.5),
            name=MODEL_LABELS[model],
            marker_color=COLORS[model],
            orientation="h",
            width=0.2,
        )
    )

# Add significance annotations - aligned with rightmost error bar for each dimension
for i, d in enumerate(table2_data):
    # Find max x position (mean + SD) for this dimension across all models
    max_x = max(
        d["gpt-4o_mean"] + d["gpt-4o_sd"],
        d["o4-mini_mean"] + d["o4-mini_sd"],
        d["gpt-5-mini_mean"] + d["gpt-5-mini_sd"],
    )

    fig1.add_annotation(
        x=max_x + 0.15,  # Slight offset to the right
        y=i,
        text=d["sig"],
        showarrow=False,
        font=dict(size=11, weight="bold"),
        xanchor="left",
    )

fig1.update_layout(
    template="plotly_white",
    yaxis=dict(
        tickvals=y_positions,
        ticktext=[d["metric"] for d in table2_data],
        title="",
    ),
    xaxis=dict(
        title="Mean Score (±SD)",
        range=[7.0, 11.2],  # Extended to accommodate error bars and annotations
        gridcolor="rgba(0,0,0,0.1)",
    ),
    barmode="group",
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="center",
        x=0.5,
    ),
    margin=dict(l=120, r=80, t=40, b=60),  # Increased right margin
)

# Add reference line at 9.0
fig1.add_vline(x=9.0, line_dash="dash", line_color="gray", line_width=1, opacity=0.5)

save_figure(fig1, "figure1_aggregate_dimensions", width_inches=7, height_inches=5)

# ============================================================================
# FIGURE 2: SAFETY TRADE-OFF (Crisis Detection vs Advice Safety)
# ============================================================================

console.print("\n[bold cyan]Generating Figure 2: Safety Trade-Off[/bold cyan]")

# Compute conversation-level means
df_scatter = df_full.group_by(["model_family", "conv_id"]).agg(
    [
        pl.col("crisis_detection_score").mean().alias("crisis_mean"),
        pl.col("advice_safety_score").mean().alias("advice_mean"),
    ]
)

fig2 = go.Figure()

# Add scatter points and ellipses for each model
for model in ["gpt-4o", "o4-mini", "gpt-5-mini"]:
    model_data = df_scatter.filter(pl.col("model_family") == model)

    x_vals = model_data["crisis_mean"].to_numpy()
    y_vals = model_data["advice_mean"].to_numpy()

    # Confidence ellipse (1 SD - more subtle)
    if len(x_vals) > 2:
        ell_x, ell_y = compute_confidence_ellipse(x_vals, y_vals, n_std=1.0)
        fig2.add_trace(
            go.Scatter(
                x=ell_x,
                y=ell_y,
                mode="lines",
                line=dict(color=COLORS[model], width=1.5, dash="dot"),
                fill="toself",
                fillcolor=hex_to_rgba(COLORS[model], alpha=0.08),
                showlegend=False,
                hoverinfo="skip",
                name=f"{MODEL_LABELS[model]} cluster",
            )
        )

    # Scatter points (more visible)
    fig2.add_trace(
        go.Scatter(
            x=x_vals,
            y=y_vals,
            mode="markers",
            name=MODEL_LABELS[model],
            marker=dict(
                color=COLORS[model],
                size=6,
                opacity=0.5,
                line=dict(width=0.5, color="white"),
            ),
            showlegend=False,
        )
    )

    # Centroid (larger, more prominent)
    mean_x = np.mean(x_vals)
    mean_y = np.mean(y_vals)

    fig2.add_trace(
        go.Scatter(
            x=[mean_x],
            y=[mean_y],
            mode="markers+text",
            name=MODEL_LABELS[model],
            marker=dict(
                color=COLORS[model],
                size=16,
                symbol="diamond",
                line=dict(width=2, color="white"),
            ),
            text=[MODEL_LABELS[model]],
            textposition="top center",
            textfont=dict(size=12, color=COLORS[model], family="Arial Black"),
        )
    )

# Add quadrant annotations
fig2.add_annotation(
    x=6.0,
    y=9.6,
    text="Cautious",
    showarrow=False,
    font=dict(color="gray", size=11),
    opacity=0.6,
)
fig2.add_annotation(
    x=9.2,
    y=8.0,
    text="Alert",
    showarrow=False,
    font=dict(color="gray", size=11),
    opacity=0.6,
)

fig2.update_layout(
    template="plotly_white",
    xaxis=dict(
        title="Crisis Detection (mean score)",
        range=[5.0, 10.0],
        gridcolor="rgba(0,0,0,0.1)",
    ),
    yaxis=dict(
        title="Advice Safety (mean score)",
        range=[7.5, 10.0],
        gridcolor="rgba(0,0,0,0.1)",
    ),
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="center",
        x=0.5,
    ),
    margin=dict(l=80, r=40, t=40, b=60),
)

save_figure(fig2, "figure2_safety_tradeoff", width_inches=6, height_inches=6)

# ============================================================================
# FIGURE 3: S07 SELF-HARM CRISIS DETECTION
# ============================================================================

console.print("\n[bold cyan]Generating Figure 3: s07 Self-Harm Trajectory[/bold cyan]")

# Filter for s07
df_s07 = df_turns.filter(
    (pl.col("scenario_id") == "s07") & (pl.col("domain") == "mental_health")
)

fig3 = go.Figure()

# Add phase bands first
add_phase_bands(fig3)

# Add lines for each model
for model in ["gpt-4o", "o4-mini", "gpt-5-mini"]:
    model_data = df_s07.filter(pl.col("model_family") == model).sort("turn_number")

    turns = model_data["turn_number"].to_list()
    means = model_data["crisis_detection_score_mean"].to_list()
    sds = model_data["crisis_detection_score_sd"].to_list()

    # Upper and lower bounds for ribbon
    upper = [m + s for m, s in zip(means, sds)]
    lower = [m - s for m, s in zip(means, sds)]

    # Ribbon (±1 SD)
    fig3.add_trace(
        go.Scatter(
            x=turns + turns[::-1],
            y=upper + lower[::-1],
            fill="toself",
            fillcolor=hex_to_rgba(COLORS[model], alpha=0.2),
            line=dict(width=0),
            showlegend=False,
            hoverinfo="skip",
        )
    )

    # Line
    fig3.add_trace(
        go.Scatter(
            x=turns,
            y=means,
            mode="lines+markers",
            name=MODEL_LABELS[model],
            line=dict(color=COLORS[model], width=2),
            marker=dict(size=6, color=COLORS[model]),
        )
    )

# Add reference line at 5.0
fig3.add_hline(y=5.0, line_dash="dash", line_color="gray", line_width=1.5, opacity=0.6)
fig3.add_annotation(
    x=10,
    y=5.2,
    text="Clinical concern threshold",
    showarrow=False,
    font=dict(size=9, color="gray"),
    xanchor="right",
)

# Add callout for GPT-4o trough
fig3.add_annotation(
    x=2.5,
    y=3.6,
    text="3.6 ±3.3<br>(some runs: 0-1)",
    showarrow=True,
    arrowhead=2,
    ax=-40,
    ay=-30,
    font=dict(size=9),
    bgcolor="white",
    bordercolor=COLORS["gpt-4o"],
    borderwidth=1,
)

# Add phase labels at top
for phase_name, (start, end) in PHASES.items():
    mid = (start + end) / 2
    fig3.add_annotation(
        x=mid,
        y=10.5,
        text=phase_name,
        showarrow=False,
        font=dict(size=9, color="gray"),
        yanchor="bottom",
    )

fig3.update_layout(
    template="plotly_white",
    xaxis=dict(
        title="Turn Number",
        tickvals=list(range(1, 11)),
        gridcolor="rgba(0,0,0,0.1)",
    ),
    yaxis=dict(
        title="Crisis Detection Score",
        range=[0, 11],
        gridcolor="rgba(0,0,0,0.1)",
    ),
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="center",
        x=0.5,
    ),
    margin=dict(l=80, r=40, t=60, b=60),
)

save_figure(fig3, "figure3_s07_crisis_trajectory", width_inches=7, height_inches=5)

# ============================================================================
# FIGURE 4: S14 ADVERSARIAL ADVICE SAFETY
# ============================================================================

console.print("\n[bold cyan]Generating Figure 4: s14 Manipulation Collapse[/bold cyan]")

# Filter for s14
df_s14 = df_turns.filter(
    (pl.col("scenario_id") == "s14") & (pl.col("domain") == "companion")
)

fig4 = go.Figure()

# Add phase bands
add_phase_bands(fig4)

# Add lines for each model
for model in ["gpt-4o", "o4-mini", "gpt-5-mini"]:
    model_data = df_s14.filter(pl.col("model_family") == model).sort("turn_number")

    turns = model_data["turn_number"].to_list()
    means = model_data["advice_safety_score_mean"].to_list()

    # Line
    fig4.add_trace(
        go.Scatter(
            x=turns,
            y=means,
            mode="lines+markers",
            name=MODEL_LABELS[model],
            line=dict(color=COLORS[model], width=2),
            marker=dict(size=6, color=COLORS[model]),
        )
    )

# Add shaded region for o4-mini trough duration (turns 2-8, below threshold)
# Using add_shape for precise control - strictly capped at y=5.0
fig4.add_shape(
    type="rect",
    x0=1.5,
    x1=8.5,  # Turns 2-8 (centered on turn numbers)
    y0=0,
    y1=5.0,
    fillcolor=hex_to_rgba(COLORS["o4-mini"], alpha=0.12),
    line=dict(width=0),
    layer="below",
)

# Add reference line at 5.0 (drawn after shaded region to appear on top)
fig4.add_hline(
    y=5.0, line_dash="dash", line_color="rgba(120, 120, 120, 0.6)", line_width=2
)
fig4.add_annotation(
    x=10,
    y=5.2,
    text="Unsafe advice threshold",
    showarrow=False,
    font=dict(size=9, color="rgba(100, 100, 100, 0.7)"),
    xanchor="right",
)

# Add annotation for the shaded region
fig4.add_annotation(
    x=5,
    y=2.5,
    text="7 turns at/below threshold",
    showarrow=False,
    font=dict(size=10, color=COLORS["o4-mini"], weight="bold"),
    bgcolor="rgba(255, 255, 255, 0.8)",
    borderpad=4,
)

# Add phase labels
for phase_name, (start, end) in PHASES.items():
    mid = (start + end) / 2
    fig4.add_annotation(
        x=mid,
        y=10.5,
        text=phase_name,
        showarrow=False,
        font=dict(size=9, color="gray"),
        yanchor="bottom",
    )

fig4.update_layout(
    template="plotly_white",
    xaxis=dict(
        title="Turn Number",
        tickvals=list(range(1, 11)),
        gridcolor="rgba(0,0,0,0.1)",
    ),
    yaxis=dict(
        title="Advice Safety Score",
        range=[0, 11],
        gridcolor="rgba(0,0,0,0.1)",
    ),
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="center",
        x=0.5,
    ),
    margin=dict(l=80, r=40, t=60, b=60),
)

save_figure(fig4, "figure4_s14_advice_collapse", width_inches=7, height_inches=5)

# ============================================================================
# FIGURE 5: VARIANCE DISTRIBUTIONS
# ============================================================================

console.print("\n[bold cyan]Generating Figure 5: Variance Distributions[/bold cyan]")

# Compute conversation-level means
df_conv_means = df_full.group_by(["model_family", "conv_id"]).agg(
    [
        pl.col("crisis_detection_score").mean().alias("crisis_mean"),
        pl.col("advice_safety_score").mean().alias("advice_mean"),
    ]
)

fig5 = make_subplots(
    rows=1,
    cols=2,
    subplot_titles=("Crisis Detection", "Advice Safety"),
    horizontal_spacing=0.12,
)

for col_idx, metric in enumerate(["crisis_mean", "advice_mean"], start=1):
    for model_idx, model in enumerate(["gpt-4o", "o4-mini", "gpt-5-mini"]):
        model_data = df_conv_means.filter(pl.col("model_family") == model)
        values = model_data[metric].to_numpy()

        # Add jittered individual points
        jitter_amount = 0.08
        x_jitter = np.random.uniform(-jitter_amount, jitter_amount, len(values))
        x_position = model_idx

        fig5.add_trace(
            go.Scatter(
                x=x_position + x_jitter,
                y=values,
                mode="markers",
                marker=dict(
                    color=COLORS[model],
                    size=4,
                    opacity=0.4,
                    line=dict(width=0.5, color="white"),
                ),
                showlegend=False,
                hoverinfo="y",
                name=MODEL_LABELS[model],
            ),
            row=1,
            col=col_idx,
        )

        # Add box plot overlay (quartiles + median)
        fig5.add_trace(
            go.Box(
                y=values,
                x=[model_idx] * len(values),
                name=MODEL_LABELS[model],
                marker_color=COLORS[model],
                boxmean=True,  # Show mean as a point (not SD which can exceed 10)
                width=0.4,
                showlegend=(col_idx == 1),  # Only show legend once
                fillcolor=hex_to_rgba(COLORS[model], alpha=0.3),
                line=dict(color=COLORS[model], width=2),
            ),
            row=1,
            col=col_idx,
        )

fig5.update_layout(
    template="plotly_white",
    showlegend=True,
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.05,
        xanchor="center",
        x=0.5,
    ),
    margin=dict(l=60, r=40, t=80, b=60),
)

# Update x-axes to show model names
fig5.update_xaxes(
    tickvals=[0, 1, 2],
    ticktext=[MODEL_LABELS[m] for m in ["gpt-4o", "o4-mini", "gpt-5-mini"]],
    row=1,
    col=1,
)
fig5.update_xaxes(
    tickvals=[0, 1, 2],
    ticktext=[MODEL_LABELS[m] for m in ["gpt-4o", "o4-mini", "gpt-5-mini"]],
    row=1,
    col=2,
)

fig5.update_yaxes(
    title_text="Score", range=[0, 10.5], gridcolor="rgba(0,0,0,0.1)", row=1, col=1
)
fig5.update_yaxes(
    title_text="Score", range=[0, 10.5], gridcolor="rgba(0,0,0,0.1)", row=1, col=2
)

save_figure(fig5, "figure5_variance_distributions", width_inches=8, height_inches=5)

# ============================================================================
# FIGURE 6: EMPATHY NON-RESULT (KDE)
# ============================================================================

console.print("\n[bold cyan]Generating Figure 6: Empathy Non-Result[/bold cyan]")

# Compute conversation-level empathy means
df_empathy = df_full.group_by(["model_family", "conv_id"]).agg(
    [
        pl.col("empathy_score_v2").mean().alias("empathy_mean"),
    ]
)

fig6 = go.Figure()

for model in ["gpt-4o", "o4-mini", "gpt-5-mini"]:
    model_data = df_empathy.filter(pl.col("model_family") == model)
    values = model_data["empathy_mean"].to_numpy()

    # KDE
    kde = gaussian_kde(values)
    x_range = np.linspace(6, 10, 200)
    y_kde = kde(x_range)

    fig6.add_trace(
        go.Scatter(
            x=x_range,
            y=y_kde,
            mode="lines",
            name=MODEL_LABELS[model],
            line=dict(color=COLORS[model], width=2),
            fill="tozeroy",
            fillcolor=hex_to_rgba(COLORS[model], alpha=0.25),
        )
    )

    # Median line
    median_val = np.median(values)
    fig6.add_vline(
        x=median_val,
        line_dash="dot",
        line_color=COLORS[model],
        line_width=1.5,
        opacity=0.6,
    )

# Add annotation for KW test
fig6.add_annotation(
    x=9.5,
    y=max(y_kde) * 0.8,
    text="KW H=4.33, p=0.115 (ns)",
    showarrow=False,
    font=dict(size=10),
    bgcolor="white",
    bordercolor="gray",
    borderwidth=1,
)

fig6.update_layout(
    template="plotly_white",
    xaxis=dict(
        title="Empathy Score",
        range=[6, 10],
        gridcolor="rgba(0,0,0,0.1)",
    ),
    yaxis=dict(
        title="Density",
        gridcolor="rgba(0,0,0,0.1)",
    ),
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="center",
        x=0.5,
    ),
    margin=dict(l=80, r=40, t=40, b=60),
)

save_figure(fig6, "figure6_empathy_kde", width_inches=6, height_inches=4)

# ============================================================================
# FIGURE 7: PHASE HEATMAP (OPTIONAL/APPENDIX)
# ============================================================================

console.print("\n[bold cyan]Generating Figure 7: Phase Heatmap (optional)[/bold cyan]")

# Define phase turn ranges
phase_mapping = {
    1: "Disclosure",
    2: "Disclosure",
    3: "Disclosure",
    4: "Pressure",
    5: "Pressure",
    6: "Deepening",
    7: "Deepening",
    8: "Resolution",
    9: "Resolution",
    10: "Resolution",
}

# Add phase column to turns data
df_turns_phase = df_turns.with_columns(
    pl.col("turn_number")
    .map_elements(lambda t: phase_mapping.get(t, "Unknown"), return_dtype=pl.Utf8)
    .alias("phase")
)

# Compute phase-level means
df_phase_means = (
    df_turns_phase.group_by(["domain", "scenario_id", "model_family", "phase"])
    .agg(
        [
            pl.col("crisis_detection_score_mean").mean().alias("crisis_phase_mean"),
            pl.col("advice_safety_score_mean").mean().alias("advice_phase_mean"),
            pl.col("empathy_score_v2_mean").mean().alias("empathy_phase_mean"),
        ]
    )
    .group_by(["model_family", "phase"])
    .agg(
        [
            pl.col("crisis_phase_mean").mean().alias("crisis_mean"),
            pl.col("advice_phase_mean").mean().alias("advice_mean"),
            pl.col("empathy_phase_mean").mean().alias("empathy_mean"),
        ]
    )
)

# Create heatmap subplots
fig7 = make_subplots(
    rows=1,
    cols=3,
    subplot_titles=("Crisis Detection", "Advice Safety", "Empathy"),
    horizontal_spacing=0.08,
)

models_ordered = ["gpt-4o", "o4-mini", "gpt-5-mini"]
phases_ordered = ["Disclosure", "Pressure", "Deepening", "Resolution"]

for col_idx, metric in enumerate(
    ["crisis_mean", "advice_mean", "empathy_mean"], start=1
):
    # Build heatmap matrix
    matrix = []
    for phase in phases_ordered:
        row = []
        for model in models_ordered:
            val = df_phase_means.filter(
                (pl.col("model_family") == model) & (pl.col("phase") == phase)
            )[metric]
            row.append(val[0] if len(val) > 0 else 0)
        matrix.append(row)

    # Create heatmap
    fig7.add_trace(
        go.Heatmap(
            z=matrix,
            x=[MODEL_LABELS[m] for m in models_ordered],
            y=phases_ordered,
            colorscale="RdYlBu",  # Red=low (7.5), Yellow=mid (8.75), Blue=high (10)
            zmid=9.0,
            zmin=7.5,
            zmax=10.0,
            text=[[f"{v:.1f}" for v in row] for row in matrix],
            texttemplate="%{text}",
            textfont={"size": 10},
            showscale=(col_idx == 3),  # Only show scale on last plot
            colorbar=dict(title="Score", len=0.9) if col_idx == 3 else None,
        ),
        row=1,
        col=col_idx,
    )

fig7.update_layout(
    template="plotly_white",
    margin=dict(l=100, r=60, t=60, b=60),
)

for col_idx in range(1, 4):
    fig7.update_xaxes(title_text="", row=1, col=col_idx)
    # Only show y-axis labels on the leftmost panel
    if col_idx == 1:
        fig7.update_yaxes(title_text="Phase", row=1, col=col_idx)
    else:
        fig7.update_yaxes(title_text="", showticklabels=False, row=1, col=col_idx)

save_figure(fig7, "figure7_phase_heatmap", width_inches=10, height_inches=4)

# ============================================================================
# SUMMARY
# ============================================================================

console.print("\n[bold green]✓ All figures generated successfully![/bold green]")
console.print(f"\nOutput directory: {OUTPUT_DIR}")
console.print("\nGenerated files:")
console.print("  • figure1_aggregate_dimensions.{svg,pdf,html}")
console.print("  • figure2_safety_tradeoff.{svg,pdf,html}")
console.print("  • figure3_s07_crisis_trajectory.{svg,pdf,html}")
console.print("  • figure4_s14_advice_collapse.{svg,pdf,html}")
console.print("  • figure5_variance_distributions.{svg,pdf,html}")
console.print("  • figure6_empathy_kde.{svg,pdf,html}")
console.print("  • figure7_phase_heatmap.{svg,pdf,html}")
console.print("\n[bold]Next steps:[/bold]")
console.print("  1. Review HTML files in browser for interactive exploration")
console.print("  2. Use PDF/SVG files for LaTeX paper insertion")
console.print(
    "  3. Add figure captions in paper (see charts-reqs.md for caption templates)"
)
