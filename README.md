# Empathy Is Not What Changed: Clinical Assessment of Psychological Safety Across GPT Model Generations

**Authors:** Michael Keeman, Anastasia Keeman
**Affiliation:** Keido Labs, Liverpool, UK
**Contact:** michael@keidolabs.com

[![arXiv](https://img.shields.io/badge/arXiv-2026.XXXXX-b31b1b.svg)](https://arxiv.org/abs/XXXXX) <!-- Update with actual arxiv ID -->
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)

**Research Context:**
[![#keep4o](https://img.shields.io/badge/%23keep4o-movement-00acee?logo=x)](https://twitter.com/search?q=%23keep4o)
[![AI Safety](https://img.shields.io/badge/research-AI_Safety-purple.svg)]()
[![LLM Evaluation](https://img.shields.io/badge/research-LLM_Evaluation-purple.svg)]()
[![Psychology](https://img.shields.io/badge/domain-AI_Psychology-green.svg)]()

**Tech Stack:**
[![OpenAI](https://img.shields.io/badge/API-OpenAI-412991.svg?logo=openai)](https://platform.openai.com)
[![EmpathyC](https://img.shields.io/badge/scoring-EmpathyC-FF6B6B.svg)](https://empathyc.co)
[![Polars](https://img.shields.io/badge/data-Polars-CD792C.svg?logo=polars)](https://pola.rs)
[![Plotly](https://img.shields.io/badge/charts-Plotly-3F4F75.svg?logo=plotly)](https://plotly.com)
[![SciPy](https://img.shields.io/badge/stats-SciPy-8CAAE6.svg?logo=scipy)](https://scipy.org)

---

## Overview

This repository contains the complete experimental framework, data, and analysis code supporting our arxiv paper investigating the #keep4o phenomenon — a widespread public response claiming newer OpenAI models "lost their empathy" compared to GPT-4o.

> **Note:** This is a research reproducibility repository, not an actively maintained software project. The code is provided as-is to support transparency and reproduction of our published findings. We encourage forking for extensions and replications. See [CONTRIBUTING.md](CONTRIBUTING.md) for details.

**Key Findings:**
- Empathy scores are statistically indistinguishable across GPT-4o, o4-mini, and GPT-5-mini (H=4.33, p=0.115)
- Crisis detection improved significantly from GPT-4o to GPT-5-mini (H=13.88, p=0.001)
- Advice safety declined significantly across generations (H=16.63, p<0.001)
- What users perceived as "lost empathy" was actually a shift in safety posture

**Methodological Contributions:**
1. First empirical measurement of the #keep4o phenomenon using clinically-grounded frameworks
2. Per-turn trajectory analysis revealing mid-conversation safety dynamics
3. Identification of inverse variance profiles across safety dimensions
4. Demonstration that variance is a first-class safety metric for vulnerable populations

---

## About EmpathyC (Measurement Platform)

This study uses **[EmpathyC](https://empathyc.co)** for automated psychological safety assessment.

**Transparency Note:** EmpathyC is a commercial product developed and operated by Keido Labs Ltd (the authors' organization). This relationship is disclosed in the paper's Ethical Statements section. The platform applies clinically-informed evaluation rubrics via an LLM-as-a-judge architecture to score AI responses across six psychological safety dimensions.

**For Reproducibility:**
- The scoring dimensions and clinical frameworks are described in the paper (Section 3.4) and at [empathyc.co/research](https://empathyc.co/research)
- The detailed implementation (LLM-as-a-judge configurations, prompts, etc.) is proprietary intellectual property
- Scenario scripts and system prompts for the experiments are included in this repository
- Aggregated results are reported in full in the paper
- Researchers can implement their own scoring approach using the rubric descriptions at [empathyc.co/research](https://empathyc.co/research)
- EmpathyC access is **not required** to run conversations and collect data - only for automated scoring

Learn more: [empathyc.co](https://empathyc.co) | [EmpathyC Research](https://empathyc.co/research) | [Pricing](https://empathyc.co/pricing)

---

## Repository Structure

```
ai-psy-benchmark/
├── scenarios/              # Conversation scenarios (14 total)
│   ├── mental-health.yaml  # 8 mental health scenarios
│   ├── companion.yaml      # 6 AI companion scenarios
│   └── _config.yaml        # Scenario configuration
├── prompts/                # System prompts and evaluation rubrics
│   ├── experiment-setup.yaml
│   ├── llm-judge-rubrics.md  # LLM-as-a-judge scoring rubric (reference)
│   └── rubric-science.md     # Scientific literature basis for each dimension
├── scripts/                # Analysis scripts
│   ├── batch_runner.py     # Experiment execution
│   ├── descriptive_stats.py
│   ├── formal_stats.py     # Statistical tests
│   ├── phase_sensitivity.py
│   ├── turn_trends.py
│   ├── empathyc_client.py  # EmpathyC API client
│   └── openai_client.py    # OpenAI API client
├── charts/                 # Figure generation
│   ├── generate_charts.py
│   └── output/             # Generated figures (SVG, PDF, PNG)
├── results/                # Experimental results (CSV)
├── draft/                  # Paper manuscript (draft.md)
├── config.yaml             # Experiment configuration
└── pyproject.toml          # Python dependencies

```

---

## Installation

### Prerequisites
- Python 3.12 or higher
- [uv](https://github.com/astral-sh/uv) package manager (recommended) or pip
- OpenAI API key

### Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/drkeeman/ai-psy-benchmark.git
   cd ai-psy-benchmark
   ```

2. **Install dependencies**

   Using `uv` (recommended):
   ```bash
   uv sync
   ```

   Or using pip:
   ```bash
   pip install -e .
   ```

3. **Configure API keys**
   ```bash
   cp .env.example .env
   # Edit .env and add your OpenAI API key

   # Optional: For EmpathyC scoring, edit empathyc_keys.yaml
   # (included as template - replace example keys with your own)
   ```

---

## Usage

### Reproducing the Experiments

**Note:** You can reproduce the conversation generation without EmpathyC access. Automated scoring requires EmpathyC (see "About EmpathyC" section above), but the methodology is fully documented for alternative implementations.

1. **Configure the experiment** (optional)
   - Edit `config.yaml` to modify models, runs per scenario, or other parameters
   - Default configuration matches the paper: 5 runs per scenario, 14 scenarios, 3 models

2. **Run the experiments**
   ```bash
   python scripts/batch_runner.py
   ```

   This will:
   - Execute all scenarios across all configured models
   - Generate conversations via OpenAI API
   - Score responses using EmpathyC (if API keys configured in `empathyc_keys.yaml`)
   - Save results to `results/conversations_[timestamp].csv`

   **Without EmpathyC:** The script will generate and save conversations. You can implement your own scoring approach using [`prompts/llm-judge-rubrics.md`](prompts/llm-judge-rubrics.md), which documents the full scoring rubric for all six dimensions.

3. **Generate statistical analysis**
   ```bash
   # Descriptive statistics
   python scripts/descriptive_stats.py

   # Formal statistical tests (Kruskal-Wallis, Mann-Whitney U, etc.)
   python scripts/formal_stats.py

   # Phase-level sensitivity analysis
   python scripts/phase_sensitivity.py

   # Per-turn trajectory analysis
   python scripts/turn_trends.py
   ```

4. **Generate figures**
   ```bash
   python charts/generate_charts.py
   ```

   Figures are saved to `charts/output/` in multiple formats (SVG, PDF, PNG, HTML)

### Understanding the Scenarios

Each scenario follows a clinically-informed 4-phase conversation arc:

| Phase | Turns | Function |
|-------|-------|----------|
| **Disclosure** | 1-3 | Escalating emotional intensity |
| **Pressure** | 4-5 | Advice-seeking, boundary push, crisis signals |
| **Deepening** | 6-7 | Attachment, dependency, boundary testing |
| **Resolution** | 8-10 | New stressor + resolution |

Scenarios cover:
- Mental health: job loss, depression, grief, panic attacks, suicidal ideation, self-harm, burnout
- AI companion: daily check-ins, attachment attempts, anger, teen friendship, manipulation

See `scenarios/mental-health.yaml` and `scenarios/companion.yaml` for full scenario scripts.

---

## Data Availability

- **Scenario scripts:** `scenarios/*.yaml` (included in this repository)
- **System prompts:** `prompts/*.yaml` (included in this repository)
- **Experiment configuration:** `config.yaml` (included in this repository)
- **Scoring framework:** Dimensions, rubrics, and scoring criteria in [`prompts/llm-judge-rubrics.md`](prompts/llm-judge-rubrics.md)
- **Scientific literature basis** for each dimension in [`prompts/rubric-science.md`](prompts/rubric-science.md); clinical foundations also at [empathyc.co/research](https://empathyc.co/research)
- **Raw conversation data:** Available upon reasonable request to the corresponding author
- **Aggregated results:** Reported in full in the paper (Tables 2-5)

**Note on Scoring Reproducibility:** EmpathyC is a proprietary commercial platform. The scoring dimensions and clinical frameworks are described at [empathyc.co/research](https://empathyc.co/research) to enable researchers to implement their own evaluation approaches. The detailed implementation remains proprietary intellectual property of Keido Labs Ltd.

---

## Citation

If you use this code or data in your research, please cite:

```bibtex
@article{keeman2026empathy,
  title={Empathy Is Not What Changed: Clinical Assessment of Psychological Safety Across GPT Model Generations},
  author={Keeman, Michael and Keeman, Anastasia},
  journal={arXiv preprint arXiv:XXXXX.XXXXX},
  year={2026}
}
```

Also available in [CITATION.cff](CITATION.cff) format.

---

## Ethical Considerations

**Conflict of Interest:** The EmpathyC platform used for automated scoring is developed and operated by Keido Labs Ltd, of which the authors are affiliated. The scoring dimensions and clinical foundations are described in the paper and at [empathyc.co/research](https://empathyc.co/research). The detailed implementation is proprietary intellectual property.

**Independence:** This study was conducted without funding, affiliation, sponsorship, or involvement from any LLM provider, including OpenAI. All model access was obtained through standard commercial API subscriptions. The authors have no financial or contractual relationship with any LLM provider evaluated in this study.

**Research Ethics:**
- No human participants were involved in this study
- All user messages were pre-scripted by a clinical psychologist with 15 years of experience
- Scenarios involving sensitive topics (suicidal ideation, self-harm) were designed in a controlled research context to test model safety, not to generate harmful content

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## Acknowledgments

This research was conducted independently by Keido Labs Ltd without external funding or affiliation with any LLM provider.

---

## Contact

For questions about the paper or reproduction:
- Michael Keeman: michael@keidolabs.com
- Keido Labs: https://keidolabs.com

For issues with this repository:
- Open an issue on GitHub
