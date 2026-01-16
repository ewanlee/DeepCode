"""
The Critic Agent - Verification Test Generation

Converts theoretical propositions into executable Python unit tests.
"""

import re
from typing import Dict, Any, List
from mcp_agent.agents.agent import Agent
from paper2sim.prompts.phase1_prompts import THE_CRITIC_PROMPT


class TheCriticAgent:
    """
    Generates verification tests from paper propositions
    
    This agent:
    - Extracts Propositions, Lemmas, Corollaries from paper
    - Converts them to Python unittest assertions
    - Creates a complete test file for verification
    """
    
    def __init__(self, llm_factory=None, server_names=None):
        """
        Initialize The Critic
        
        Args:
            llm_factory: LLM factory for agent creation
            server_names: MCP servers to use
        """
        self.llm_factory = llm_factory
        self.server_names = server_names or ["filesystem"]
        
        self.agent = Agent(
            name="TheCriticAgent",
            instruction=THE_CRITIC_PROMPT,
            server_names=self.server_names
        )
    
    async def generate_verification_tests(
        self,
        paper_path: str,
        game_model: Dict[str, Any],
        output_path: str = None
    ) -> str:
        """
        Generate verification test file
        
        Args:
            paper_path: Path to paper markdown file
            game_model: Game model from The Theorist
            output_path: Optional path to save test file
        
        Returns:
            test_code: Complete Python test file as string
        """
        # Build prompt
        game_model_str = self._format_game_model(game_model)
        
        prompt = f"""Generate verification tests for this paper.

Paper location: {paper_path}

Game Model:
{game_model_str}

Tasks:
1. Extract all Propositions, Lemmas, and Corollaries from the paper
2. Convert each to a Python unittest
3. Tests should verify LLM agents at Temperature=0 reproduce the theoretical results
4. Include appropriate statistical tests for stochastic outcomes

Return a complete test_verification.py file."""
        
        # Execute generation
        async with self.agent:
            llm = await self.agent.attach_llm(self.llm_factory)
            
            result = await llm.generate_str(
                message=prompt,
                request_params={
                    "maxTokens": 6000,
                    "temperature": 0.2,
                }
            )
        
        # Extract code
        test_code = self._extract_python_code(result)
        
        # Save if output path specified
        if output_path:
            with open(output_path, 'w') as f:
                f.write(test_code)
            print(f"Verification tests saved to {output_path}")
        
        return test_code
    
    def _format_game_model(self, game_model: Dict[str, Any]) -> str:
        """Format game model for prompt context"""
        import json
        return json.dumps(game_model, indent=2)
    
    def _extract_python_code(self, text: str) -> str:
        """Extract Python code from markdown blocks"""
        # Look for python code blocks
        pattern = r"```python\n(.*?)```"
        matches = re.findall(pattern, text, re.DOTALL)
        
        if matches:
            # Return the largest code block (likely the complete file)
            return max(matches, key=len)
        
        # Fallback: return everything if no code blocks found
        return text
    
    def extract_propositions(self, paper_text: str) -> List[Dict[str, str]]:
        """
        Extract propositions from paper text
        
        Args:
            paper_text: Full paper content
        
        Returns:
            propositions: List of {type, number, statement}
        """
        propositions = []
        
        # Regex patterns for common theorem-like environments
        patterns = [
            r"(Proposition|Lemma|Corollary|Theorem)\s+(\d+)[.:]?\s+(.*?)(?=\n\n|Proof|$)",
            r"\*\*(Proposition|Lemma|Corollary|Theorem)\s+(\d+)\*\*[.:]?\s+(.*?)(?=\n\n|Proof|$)",
        ]
        
        for pattern in patterns:
            matches = re.finditer(pattern, paper_text, re.DOTALL | re.IGNORECASE)
            for match in matches:
                prop_type = match.group(1)
                prop_number = match.group(2)
                statement = match.group(3).strip()
                
                propositions.append({
                    "type": prop_type,
                    "number": prop_number,
                    "statement": statement
                })
        
        return propositions
