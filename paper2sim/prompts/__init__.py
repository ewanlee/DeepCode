# Paper2Sim Prompts Module
"""
Prompts for Paper2Sim agents organized by phase and task type.

Model Assignment:
- Planning model prompts: Used for analysis, extraction, diagnosis tasks
- Implementation model prompts: Used for code generation tasks
"""

# Phase 1: Deconstruction
from .phase1_prompts import (
    THE_THEORIST_PROMPT,           # Planning: Game model extraction
    THE_CRITIC_ANALYSIS_PROMPT,    # Planning: Extract theoretical results
    THE_CRITIC_CODING_PROMPT,      # Implementation: Generate test code
)

# Phase 2: Architecture & Coding
from .phase2_prompts import (
    THE_ARCHITECT_PROMPT,          # Planning: Design architecture
    THE_ENGINEER_PROMPT,           # Implementation: Generate simulation code
)

# Phase 3: Verification & Calibration
from .phase3_prompts import (
    THE_QA_SPECIALIST_PROMPT,      # Legacy combined prompt
    THE_QA_DIAGNOSIS_PROMPT,       # Planning: Diagnose test failures
    THE_QA_FIX_PROMPT,             # Implementation: Generate fixes
    DEBUGGING_GUIDE_PROMPT,        # Reference: Debugging patterns
)

# Phase 4: Advanced Emergence (optional)
from .phase4_prompts import (
    THE_HISTORIAN_PROMPT,          # Memory systems
    THE_NARRATIVE_DESIGNER_PROMPT, # Language/communication
    THE_RED_TEAMER_PROMPT,         # Adversarial testing
)

__all__ = [
    # Phase 1
    "THE_THEORIST_PROMPT",
    "THE_CRITIC_ANALYSIS_PROMPT",
    "THE_CRITIC_CODING_PROMPT",
    # Phase 2
    "THE_ARCHITECT_PROMPT",
    "THE_ENGINEER_PROMPT",
    # Phase 3
    "THE_QA_SPECIALIST_PROMPT",
    "THE_QA_DIAGNOSIS_PROMPT",
    "THE_QA_FIX_PROMPT",
    "DEBUGGING_GUIDE_PROMPT",
    # Phase 4
    "THE_HISTORIAN_PROMPT",
    "THE_NARRATIVE_DESIGNER_PROMPT",
    "THE_RED_TEAMER_PROMPT",
]