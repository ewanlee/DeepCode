"""
Paper2Sim: Hybrid OR/LLM Simulation Engine

Automatically converts operations research/game theory papers into 
high-fidelity simulations with LLM agents.

Core Principle: Environment as Law (Math), Agent as Brain (LLM)
"""

__version__ = "0.1.0"

from paper2sim.workflows.paper2sim_workflow import Paper2SimWorkflow
from paper2sim.agents import (
    TheTheoristAgent,
    TheCriticAgent,
    TheArchitectAgent,
    TheEngineerAgent,
    TheQASpecialistAgent,
)

__all__ = [
    'Paper2SimWorkflow',
    'TheTheoristAgent',
    'TheCriticAgent',
    'TheArchitectAgent',
    'TheEngineerAgent',
    'TheQASpecialistAgent',
]
