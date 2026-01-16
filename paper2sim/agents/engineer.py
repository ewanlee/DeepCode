"""
The Engineer Agent - Code Implementation

Implements the simulation code based on The Architect's design.
"""

import os
from typing import Dict, Any
from mcp_agent.agents.agent import Agent
from mcp_agent.workflows.llm.augmented_llm import RequestParams
from paper2sim.prompts.phase2_prompts import THE_ENGINEER_PROMPT


class TheEngineerAgent:
    """
    Implements simulation code from architecture
    
    Generates:
    - environment.py (game environment)
    - agents.py (LLM agents)
    - runner.py (simulation orchestration)
    - config.py (parameters)
    - main.py (entry point)
    
    Model Assignment: Uses IMPLEMENTATION model (code generation only)
    """
    
    def __init__(self, llm_factory=None, server_names=None):
        """
        Initialize The Engineer
        
        Args:
            llm_factory: LLM factory for agent creation (should be implementation_factory)
            server_names: MCP servers to use
        
        Note: This agent performs code generation only, no analysis.
              Should use the implementation_model for best results.
        """
        self.llm_factory = llm_factory  # Implementation model for code generation
        self.server_names = server_names or ["code-implementation"]
        
        self.agent = Agent(
            name="TheEngineerAgent",
            instruction=THE_ENGINEER_PROMPT,
            server_names=self.server_names
        )
    
    async def implement_simulation(
        self,
        architecture: Dict[str, Any],
        game_model: Dict[str, Any],
        verification_tests: str,
        output_dir: str
    ) -> Dict[str, str]:
        """
        Implement complete simulation codebase
        
        Args:
            architecture: Design from The Architect
            game_model: Game model from The Theorist
            verification_tests: Tests from The Critic
            output_dir: Where to write code files
        
        Returns:
            generated_files: Dict mapping filename to path
        """
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        # Build implementation prompt
        import json
        arch_str = json.dumps(architecture, indent=2)
        game_str = json.dumps(game_model, indent=2)
        
        prompt = f"""Implement the simulation code.

Architecture Specification:
{arch_str}

Game Model:
{game_str}

Verification Tests:
{verification_tests}

Output Directory: {output_dir}

Tasks:
1. Implement environment.py (GameEnvironment class)
2. Implement agents.py (LLMAgent classes with system prompts)
3. Implement runner.py (SimulationRunner)
4. Implement config.py (game parameters)
5. Implement main.py (entry point)
6. Copy verification tests to test_verification.py

Use write_file tool to create each file in {output_dir}/

Requirements:
- Environment must be pure Python (no LLM calls)
- Agents use LLM for decisions
- Code must be production-ready with type hints and docstrings
- Copy formulas exactly from game model"""
        
        # Execute implementation
        async with self.agent:
            llm = await self.agent.attach_llm(self.llm_factory)
            
            # Set workspace to output directory
            await self.agent.call_tool("set_workspace", {"workspace_path": output_dir})
            
            params = RequestParams(
                maxTokens=16000,
                temperature=0.2,
                max_iterations=20,  # Allow multiple tool calls
            )
            
            result = await llm.generate_str(
                message=prompt,
                request_params=params
            )
        
        # Collect generated files
        generated_files = {}
        expected_files = [
            "environment.py",
            "agents.py",
            "runner.py",
            "config.py",
            "main.py",
            "test_verification.py"
        ]
        
        for filename in expected_files:
            filepath = os.path.join(output_dir, filename)
            if os.path.exists(filepath):
                generated_files[filename] = filepath
                print(f"✓ Generated {filename}")
            else:
                print(f"⚠ Missing {filename}")
        
        return generated_files
