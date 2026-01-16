# Paper2Sim: Hybrid OR/LLM Simulation Engine

**Automatically convert operations research/game theory papers into high-fidelity simulations with LLM agents.**

## 🎯 Core Principle

**Environment as Law (Math), Agent as Brain (LLM)**

- **Environment**: Deterministic mathematical model (pure Python, no LLM)
- **Agent**: Cognitive decision-maker (LLM-powered, behavioral)

## 🚀 Quick Start

```bash
# Run complete pipeline
python -m paper2sim.main --paper path/to/paper.md

# Specify output location
python -m paper2sim.main --paper paper.md --output ./my_simulations --name my_sim

# Enable advanced features (Phase 4)
python -m paper2sim.main --paper paper.md --phase4
```

## 📊 Pipeline Overview

### Phase 1: Deconstruction
- **The Theorist**: Extracts game model <N, S, A, U>
- **The Critic**: Generates verification tests from Propositions

### Phase 2: Architecture & Coding
- **The Architect**: Designs simulation architecture
- **The Engineer**: Implements production-ready code

### Phase 3: Verification & Calibration
- **The QA Specialist**: Calibrates agents to match theory (Temperature=0)

### Phase 4: Advanced Emergence (Optional)
- **The Historian**: Adds long-term memory (path dependence)
- **The Narrative Designer**: Enables linguistic communication
- **The Red Teamer**: Tests mechanism robustness

## 📁 Output Structure

```
paper2sim_output/
└── my_project/
    ├── game_model.json              # Extracted game structure
    ├── architecture.json             # System design
    ├── test_verification.py          # Verification tests
    ├── calibration_report.json       # QA results
    └── simulation/                   # Generated code
        ├── environment.py            # Game environment (white-box)
        ├── agents.py                 # LLM agents (gray-box)
        ├── runner.py                 # Simulation orchestration
        ├── config.py                 # Parameters
        └── main.py                   # Entry point
```

## 🔬 Verification Philosophy

**Calibration is mandatory** before enabling advanced features:

1. At Temperature=0, agents must reproduce theoretical Propositions
2. This validates that LLMs understand the game logic
3. Only then can we explore behavioral complexity (Temperature>0, memory, language)

## 🌟 Phase 4 Features

Once calibrated, enable:

- **Cognitive Path Dependence**: Agents remember past experiences
- **Semantic Layer**: Natural language communication with framing effects
- **Red Teaming**: Adversarial testing for mechanism exploits

## 📚 Example

```python
from paper2sim.workflows.paper2sim_workflow import Paper2SimWorkflow
from utils.llm_utils import get_preferred_llm_class

# Initialize
workflow = Paper2SimWorkflow(
    llm_factory=get_preferred_llm_class(),
    output_base_dir="./output"
)

# Run pipeline
results = await workflow.run_full_pipeline(
    paper_path="papers/physician_testing.md",
    project_name="physician_sim",
    enable_phase4=False  # Calibrate first!
)

if results['is_calibrated']:
    print("✅ Ready to run simulations!")
```

## 🎓 Supported Paper Types

- **Signaling games** (e.g., physician testing, education signaling)
- **Screening games** (e.g., insurance markets)
- **Mechanism design** (e.g., auctions, matching)
- **Repeated games** (e.g., trust, cooperation)
- **Bayesian games** (information asymmetry)

## 🔧 Requirements

- Python 3.10+
- MCP Agent framework (from main DeepCode branch)
- LLM API (OpenAI/Anthropic/Google)

See `requirements.txt` for full dependencies.

## 📖 Documentation

Detailed prompts and specifications:
- Phase 1: `paper2sim/prompts/phase1_prompts.py`
- Phase 2: `paper2sim/prompts/phase2_prompts.py`
- Phase 3: `paper2sim/prompts/phase3_prompts.py`
- Phase 4: `paper2sim/prompts/phase4_prompts.py`

## 🤝 Contributing

This is part of the DeepCode project. Built on the `paper2sim` branch.

## 📄 License

Same as DeepCode main project.

## 🔗 References

Based on the Paper2Sim PRD (see `paper2sim_prd.md` in project root).

---

**Built on DeepCode framework** | **Branch: paper2sim**
