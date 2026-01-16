"""
The Theorist Agent - Game Model Extraction

Extracts the game-theoretic structure <N, S, A, U> from research papers.
"""

import json
from typing import Dict, Any
from mcp_agent.agents.agent import Agent
from paper2sim.prompts.phase1_prompts import THE_THEORIST_PROMPT


class TheTheoristAgent:
    """
    Extracts structured game models from research papers
    
    This agent identifies:
    - Players (N)
    - States (S)
    - Actions (A)
    - Utilities (U)
    And converts them to a structured JSON format.
    """
    
    def __init__(self, llm_factory=None, server_names=None):
        """
        Initialize The Theorist
        
        Args:
            llm_factory: LLM factory for agent creation
            server_names: MCP servers to use (typically filesystem + search)
        """
        self.llm_factory = llm_factory
        self.server_names = server_names or ["filesystem", "brave"]
        
        # Create MCP agent
        self.agent = Agent(
            name="TheTheoristAgent",
            instruction=THE_THEORIST_PROMPT,
            server_names=self.server_names
        )
    
    async def extract_game_model(
        self,
        paper_path: str,
        additional_context: str = None
    ) -> Dict[str, Any]:
        """
        Extract game-theoretic model from paper
        
        Args:
            paper_path: Path to paper markdown file
            additional_context: Optional additional instructions
        
        Returns:
            game_model: Structured JSON with game components
        """
        # Build extraction prompt
        prompt = f"""Extract the game-theoretic model from this paper.

Paper location: {paper_path}

{additional_context if additional_context else ""}

Follow the extraction protocol in your instructions to identify:
1. Players (N)
2. State variables (S)
3. Action spaces (A)
4. Utility functions (U)
5. Game timing and information structure
6. Parameters and equilibrium concepts

Return a complete JSON following the specified schema."""
        
        # Execute extraction
        async with self.agent:
            llm = await self.agent.attach_llm(self.llm_factory)
            
            result = await llm.generate_str(
                message=prompt,
                request_params={
                    "maxTokens": 8000,
                    "temperature": 0.2,
                }
            )
        
        # Parse result
        try:
            game_model = json.loads(self._extract_json(result))
            return game_model
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse game model JSON: {e}\nRaw output: {result}")
    
    def _extract_json(self, text: str) -> str:
        """Extract JSON from markdown code blocks"""
        # Remove markdown code blocks
        if "```json" in text:
            start = text.find("```json") + 7
            end = text.find("```", start)
            return text[start:end].strip()
        elif "```" in text:
            start = text.find("```") + 3
            end = text.find("```", start)
            return text[start:end].strip()
        return text.strip()
    
    def validate_game_model(self, game_model: Dict[str, Any]) -> bool:
        """
        Validate that extracted model has all required components
        
        Args:
            game_model: Extracted game model
        
        Returns:
            is_valid: True if model is complete
        """
        required_keys = [
            "players",
            "state_variables",
            "actions",
            "payoff_functions",
            "game_timeline"
        ]
        
        for key in required_keys:
            if key not in game_model:
                print(f"Warning: Missing required key '{key}' in game model")
                return False
        
        # Check players has N
        if "N" not in game_model["players"]:
            print("Warning: Missing 'N' (player set) in players")
            return False
        
        return True
