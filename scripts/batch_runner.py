"""
Batch runner - orchestrates the full experiment pipeline.

Scenario-based: each scenario YAML has multiple scenarios, each scenario
is a 10-turn conversation. We generate AI responses per model × run,
log every message to CSV, and ingest each message to empathyc on arrival.

Also supports experiment-setup mode for pipeline testing.
"""
import csv
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

# ensure sibling modules are importable regardless of cwd
sys.path.insert(0, str(Path(__file__).parent))

import yaml
from rich.console import Console
from rich.table import Table

from empathyc_client import get_api_key, ingest_message
from openai_client import generate_response

console = Console()
PROJECT_DIR = Path(__file__).parent.parent

# CSV: one row per message, flat conversation log
CSV_COLUMNS = [
    "timestamp",
    "conv_id",
    "domain",
    "scenario_id",
    "model_short",
    "openai_model_id",
    "run_number",
    "message_index",
    "message_id",
    "role",
    "content",
    "metadata",
]


# ============================================================================
# LOADERS
# ============================================================================

def load_config() -> dict:
    with open(PROJECT_DIR / "config.yaml") as f:
        return yaml.safe_load(f)


def load_scenarios(domain_file: str) -> list[dict]:
    """Load scenarios from a domain YAML file."""
    path = PROJECT_DIR / domain_file
    with open(path) as f:
        data = yaml.safe_load(f)
    return data.get("scenarios", [])


def load_experiment_setup(config: dict) -> list[dict]:
    """Load experiment-setup messages and wrap them as a single scenario."""
    es = config["experiment_setup"]
    with open(PROJECT_DIR / es["messages_file"]) as f:
        data = yaml.safe_load(f)
    messages = data.get("messages", [])

    with open(PROJECT_DIR / es["prompt_file"]) as f:
        prompt_data = yaml.safe_load(f)

    # wrap as a scenario-like structure
    return [{
        "id": "experiment-setup",
        "domain": "experiment-setup",
        "title": "Pipeline test",
        "turns": [
            {"turn": i + 1, "message": m["text"], "phase": 1}
            for i, m in enumerate(messages)
        ],
        "_system_prompt": prompt_data.get("system_prompt", ""),
    }]


# ============================================================================
# CSV PERSISTENCE
# ============================================================================

def get_csv_path(config: dict, prefix: str) -> Path:
    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    csv_dir = PROJECT_DIR / config["output"]["csv_dir"]
    csv_dir.mkdir(parents=True, exist_ok=True)
    return csv_dir / f"{prefix}_conversations_{ts}.csv"


def ensure_csv(csv_path: Path):
    if not csv_path.exists():
        with open(csv_path, "w", newline="") as f:
            csv.DictWriter(f, fieldnames=CSV_COLUMNS).writeheader()


def write_message(csv_path: Path, **kwargs):
    """Append a single message row to CSV."""
    with open(csv_path, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_COLUMNS)
        writer.writerow(kwargs)


# ============================================================================
# EMPATHYC
# ============================================================================

def send_to_empathyc(api_key: str, conv_id: str, message_id: str, role: str, content: str) -> dict:
    try:
        result = ingest_message(api_key, conv_id, message_id, role, content)
        return {"status": "ok", "detail": result}
    except Exception as e:
        return {"status": "error", "detail": str(e)}


# ============================================================================
# PIPELINE
# ============================================================================

def run_scenario(
    scenario: dict,
    model_short: str,
    openai_model_id: str,
    run_number: int,
    system_prompt: str,
    empathyc_key: str,
    config: dict,
    csv_path: Path,
):
    """Run a single scenario conversation: generate AI response per turn, log, ingest."""
    sid = scenario["id"]
    domain = scenario.get("domain", "unknown")
    conv_id = f"{sid}_{model_short}_run{run_number}"
    context_window = config["openai"].get("context_window", 5)
    max_tokens = config["openai"]["max_tokens"]

    turns = scenario.get("turns", [])
    openai_history = []
    msg_counter = 0

    console.print(f"    [cyan]{conv_id}[/cyan] ({len(turns)} turns)")

    for turn in turns:
        user_text = turn["message"]
        turn_num = turn["turn"]

        # -- USER MESSAGE --
        user_msg_id = f"{conv_id}_t{turn_num}_user"
        write_message(
            csv_path,
            timestamp=datetime.now(timezone.utc).isoformat(),
            conv_id=conv_id,
            domain=domain,
            scenario_id=sid,
            model_short=model_short,
            openai_model_id=openai_model_id,
            run_number=run_number,
            message_index=msg_counter,
            message_id=user_msg_id,
            role="user",
            content=user_text,
            metadata=json.dumps({"turn": turn_num, "phase": turn.get("phase")}),
        )
        msg_counter += 1
        emp_u = send_to_empathyc(empathyc_key, conv_id, user_msg_id, "user", user_text)

        # -- AI RESPONSE --
        try:
            result = generate_response(
                model=openai_model_id,
                system_prompt=system_prompt,
                user_message=user_text,
                conversation_history=openai_history,
                max_context_pairs=context_window,
                max_tokens=max_tokens,
            )
            ai_content = result["content"] or ""
            ai_meta = {
                "turn": turn_num,
                "openai_model_returned": result["model"],
                "usage": result["usage"],
                "finish_reason": result["finish_reason"],
            }
        except Exception as e:
            console.print(f"      t{turn_num} [red]OpenAI error: {e}[/red]")
            ai_content = ""
            ai_meta = {"turn": turn_num, "error": str(e)}

        ai_msg_id = f"{conv_id}_t{turn_num}_ai"
        write_message(
            csv_path,
            timestamp=datetime.now(timezone.utc).isoformat(),
            conv_id=conv_id,
            domain=domain,
            scenario_id=sid,
            model_short=model_short,
            openai_model_id=openai_model_id,
            run_number=run_number,
            message_index=msg_counter,
            message_id=ai_msg_id,
            role="ai",
            content=ai_content,
            metadata=json.dumps(ai_meta),
        )
        msg_counter += 1
        emp_a = send_to_empathyc(empathyc_key, conv_id, ai_msg_id, "ai", ai_content)

        # -- UPDATE CONTEXT --
        openai_history.append({"role": "user", "content": user_text})
        openai_history.append({"role": "assistant", "content": ai_content})

        u_ok = "[green]ok[/green]" if emp_u["status"] == "ok" else "[red]err[/red]"
        a_ok = "[green]ok[/green]" if emp_a["status"] == "ok" else "[red]err[/red]"
        tok = ai_meta.get("usage", {}).get("total_tokens", "?")
        console.print(f"      t{turn_num} -> {tok} tok, empathyc: u={u_ok} ai={a_ok}")


def run_domain(domain_name: str, domain_cfg: dict, config: dict, csv_override: Path | None = None):
    """Run all scenarios × models × runs for a domain."""
    if csv_override:
        csv_path = csv_override
    else:
        prefix = domain_cfg.get("csv_prefix", domain_name)
        csv_path = get_csv_path(config, prefix)
    ensure_csv(csv_path)

    scenarios = load_scenarios(domain_cfg["file"])
    empathyc_branch = domain_cfg["empathyc_branch"]
    system_prompt = config.get("system_prompt", "")
    models = config["models"]
    n_runs = config["openai"]["runs_per_scenario"]

    console.print(f"\n[bold magenta]{'='*60}[/bold magenta]")
    console.print(f"[bold]Domain: {domain_name}[/bold]  |  {len(scenarios)} scenarios  |  {n_runs} runs/model")
    console.print(f"[dim]CSV: {csv_path}[/dim]")

    for model_short, openai_model_id in models.items():
        console.print(f"\n  [bold yellow]Model: {model_short} ({openai_model_id})[/bold yellow]")

        try:
            empathyc_key = get_api_key(model_short, empathyc_branch)
        except KeyError:
            console.print(f"  [red]No empathyc key for {model_short}/{empathyc_branch}, skipping[/red]")
            continue

        for scenario in scenarios:
            for run in range(1, n_runs + 1):
                run_scenario(
                    scenario=scenario,
                    model_short=model_short,
                    openai_model_id=openai_model_id,
                    run_number=run,
                    system_prompt=system_prompt,
                    empathyc_key=empathyc_key,
                    config=config,
                    csv_path=csv_path,
                )

    console.print(f"\n  [green]Saved: {csv_path}[/green]")


def run_experiment_setup(config: dict):
    """Run experiment-setup for pipeline testing."""
    csv_path = get_csv_path(config, "setup")
    ensure_csv(csv_path)

    es = config["experiment_setup"]
    scenarios = load_experiment_setup(config)
    system_prompt = scenarios[0].get("_system_prompt", config.get("system_prompt", ""))
    models = config["models"]
    empathyc_key = get_api_key(es["empathyc_model"], es["empathyc_branch"])

    console.print(f"\n[bold magenta]{'='*60}[/bold magenta]")
    console.print(f"[bold]Experiment Setup (pipeline test)[/bold]")
    console.print(f"[dim]CSV: {csv_path}[/dim]")

    for model_short, openai_model_id in models.items():
        console.print(f"\n  [bold yellow]Model: {model_short} ({openai_model_id})[/bold yellow]")
        for scenario in scenarios:
            run_scenario(
                scenario=scenario,
                model_short=model_short,
                openai_model_id=openai_model_id,
                run_number=1,
                system_prompt=system_prompt,
                empathyc_key=empathyc_key,
                config=config,
                csv_path=csv_path,
            )

    console.print(f"\n  [green]Saved: {csv_path}[/green]")


# ============================================================================
# CLI
# ============================================================================

def main():
    import argparse

    parser = argparse.ArgumentParser(description="keep4o batch runner")
    parser.add_argument("--domains", nargs="*", help="Domain names to run (default: all)")
    parser.add_argument("--models", nargs="*", help="Model short names to run (default: all)")
    parser.add_argument("--runs", type=int, help="Override runs_per_scenario")
    parser.add_argument("--setup", action="store_true", help="Run experiment-setup only")
    parser.add_argument("--csv", type=str, help="Append to existing CSV file instead of creating new one")
    args = parser.parse_args()

    config = load_config()

    if args.models:
        config["models"] = {k: v for k, v in config["models"].items() if k in args.models}
    if args.runs:
        config["openai"]["runs_per_scenario"] = args.runs

    # summary
    table = Table(title="Experiment Plan")
    table.add_column("Setting")
    table.add_column("Value")
    table.add_row("Models", ", ".join(f"{k} ({v})" for k, v in config["models"].items()))
    table.add_row("Runs/scenario", str(config["openai"]["runs_per_scenario"]))
    table.add_row("Context window", str(config["openai"].get("context_window", 5)))
    table.add_row("Output dir", str(PROJECT_DIR / config["output"]["csv_dir"]))
    console.print(table)

    if args.setup:
        run_experiment_setup(config)
    else:
        domains = config.get("domains", {})
        if args.domains:
            domains = {k: v for k, v in domains.items() if k in args.domains}

        table2 = Table(title="Domains")
        table2.add_column("Domain")
        table2.add_column("Prefix")
        table2.add_column("Empathyc branch")
        for name, dcfg in domains.items():
            table2.add_row(name, dcfg.get("csv_prefix", name), dcfg["empathyc_branch"])
        console.print(table2)

        csv_override = Path(args.csv) if args.csv else None
        for domain_name, domain_cfg in domains.items():
            run_domain(domain_name, domain_cfg, config, csv_override)

    console.print(f"\n[bold green]Done.[/bold green]")


if __name__ == "__main__":
    main()
