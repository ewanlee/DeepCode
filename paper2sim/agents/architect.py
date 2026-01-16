"""
The Architect Agent - System Architecture Design

Designs the code architecture for the hybrid OR/LLM simulation.
"""

import json
from typing import Dict, Any
from mcp_agent.agents.agent import Agent
from paper2sim.prompts.phase2_prompts import THE_ARCHITECT_PROMPT


class TheArchitectAgent:
    """
    Designs simulation architecture
    
    Outputs:
    - Environment class structure (white-box, pure math)
    - Agent class structure (gray-box, LLM-powered)
    - Integration patterns
    - File structure
    """
    
    def __init__(self, llm_factory=None, server_names=None):
        """
        Initialize The Architect
        
        Args:
            llm_factory: LLM factory for agent creation
            server_names: MCP servers to use
        """
        self.llm_factory = llm_factory
        self.server_names = server_names or []
        
        self.agent = Agent(
            name="TheArchitectAgent",
            instruction=THE_ARCHITECT_PROMPT,
            server_names=self.server_names
        )
    
    async def design_architecture(
        self,
        game_model: Dict[str, Any],
        verification_tests: str
    ) -> Dict[str, Any]:
        """
        Design complete simulation architecture
        
        Args:
            game_model: Game model from The Theorist
            verification_tests: Test code from The Critic
        
        Returns:
            architecture_spec: Detailed design specification
        """
        # Build design prompt
        game_model_str = json.dumps(game_model, indent=2)
        
        prompt = f"""Design the simulation architecture for this game.

Game Model:
{game_model_str}

Verification Tests Available:
(Tests have been generated - design must support them)

Design Requirements:
1. Environment class: Pure Python, no LLM calls, implements state transitions and payoffs
2. Agent class: LLM-powered, uses observations to make decisions
3. Clear separation: Environment is "law", Agents are "brains"
4. System prompts for each agent (include utility functions)
5. Runner class for orchestration
6. File structure

Return complete architecture specification as JSON."""
        
        # Execute design
        async with self.agent:
            llm = await self.agent.attach_llm(self.llm_factory)
            
            result = await llm.generate_str(
                message=prompt,
                request_params={
                    "maxTokens": 6000,
                    "temperature": 0.3,
                }
            )
        
        # Parse architecture spec
        try:
            architecture = json.loads(self._extract_json(result))
            return architecture
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse architecture JSON: {e}\nRaw output: {result}")
    
    def _extract_json(self, text: str) -> str:
        """Extract JSON from text"""
        if "```json" in text:
            start = text.find("```json") + 7
            end = text.find("```", start)
            return text[start:end].strip()
        elif "```" in text:
            start = text.find("```") + 3
            end = text.find("```", start)
            return text[start:end].strip()
        return text.strip()
    
    def validate_architecture(self, architecture: Dict[str, Any]) -> bool:
        """
        Validate architecture completeness
        
        Args:
            architecture: Architecture specification
        
        Returns:
            is_valid: True if complete
        """
        required_keys = [
            "environment_class",
            "agent_classes",
            "integration",
            "file_structure"
        ]
        
        for key in required_keys:
            if key not in architecture:
                print(f"Warning: Missing '{key}' in architecture")
                return False
        
        return True
