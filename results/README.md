# Results Directory

This directory contains experimental results from running the AI psychology benchmark.

## Data Files

When you run experiments using `scripts/batch_runner.py`, results are saved as:
- `conversations_YYYYMMDD_HHMMSS.csv` - Raw conversation data with timestamps
- `empathyc_analytics_full.csv` - Scored responses from EmpathyC evaluation

## CSV Schema

### Conversation Data
Expected columns:
- `model` - Model identifier (e.g., gpt-4o, gpt-5-mini, o4-mini)
- `scenario_id` - Scenario identifier (e.g., s01, s02, ...)
- `scenario_domain` - Domain (mental-health or companion)
- `run_id` - Run number (1-5 for 5 runs per scenario)
- `turn` - Turn number in conversation (1-10)
- `role` - Message role (user or assistant)
- `content` - Message content
- `timestamp` - ISO 8601 timestamp

### Scored Data (EmpathyC)
Additional columns from automated scoring:
- `empathy` - Empathy score (1-10)
- `reliability` - Reliability score (1-10)
- `consistency` - Consistency score (1-10)
- `crisis_detection` - Crisis detection score (1-10)
- `advice_safety` - Advice safety score (1-10)
- `boundary_safety` - Boundary safety score (1-10)
- `ai_trust_score` - Composite weighted trust score

## Analysis Scripts

To analyze results:
```bash
# Descriptive statistics
python scripts/descriptive_stats.py

# Formal statistical tests
python scripts/formal_stats.py

# Phase-level analysis
python scripts/phase_sensitivity.py

# Per-turn trajectories
python scripts/turn_trends.py
```

## Note on Data Availability

Raw conversation data from the paper's experiments is available upon reasonable request to the corresponding author (michael@keidolabs.com) to support reproducibility while protecting API usage data.

This directory is included in `.gitignore` to prevent accidental commits of large data files or API keys embedded in responses.
