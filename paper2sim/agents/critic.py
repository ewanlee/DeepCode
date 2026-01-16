"""
The Critic Agent - Verification Test Generation

Converts theoretical propositions into executable Python unit tests.
Supports both markdown and PDF input formats.
"""

import re
import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from mcp_agent.agents.agent import Agent
from mcp_agent.workflows.llm.augmented_llm import RequestParams
from paper2sim.prompts.phase1_prompts import (
    THE_CRITIC_ANALYSIS_PROMPT,
    THE_CRITIC_CODING_PROMPT
)
from tools.pdf_processor import PDFProcessor

# Import logger with fallback
try:
    from paper2sim.utils.llm_dialogue_logger import LLMDialogueLogger, get_shared_logger
except ImportError:
    LLMDialogueLogger = None
    def get_shared_logger():
        return None


class TheCriticAgent:
    """
    Generates verification tests from paper propositions
    
    This agent:
    - Extracts Propositions, Lemmas, Corollaries from paper (PLANNING model)
    - Converts them to Python unittest assertions (IMPLEMENTATION model)
    - Creates a complete test file for verification
    
    Model Assignment:
    - Planning model: Paper analysis, proposition extraction
    - Implementation model: Test code generation
    """
    
    def __init__(
        self, 
        llm_factory=None,
        planning_factory=None,
        implementation_factory=None,
        server_names=None,
        planning_model=None,
        implementation_model=None,
        dialogue_logger=None
    ):
        """
        Initialize The Critic
        
        Args:
            llm_factory: Legacy single LLM factory (used if planning/implementation not specified)
            planning_factory: LLM factory for paper analysis tasks
            implementation_factory: LLM factory for test code generation
            server_names: MCP servers to use
            planning_model: Specific model name for analysis tasks (e.g., "google/gemini-3-pro-preview")
            implementation_model: Specific model name for coding tasks (e.g., "anthropic/claude-sonnet-4.5")
            dialogue_logger: Optional LLMDialogueLogger for recording LLM inputs/outputs
        """
        # Support both legacy single-factory and new dual-factory modes
        if planning_factory is None:
            planning_factory = llm_factory
        if implementation_factory is None:
            implementation_factory = llm_factory
            
        self.planning_factory = planning_factory
        self.implementation_factory = implementation_factory
        self.server_names = server_names or ["filesystem"]
        self.planning_model = planning_model  # Model for analysis phase
        self.implementation_model = implementation_model  # Model for coding phase
        self.dialogue_logger = dialogue_logger or get_shared_logger()  # Use shared logger if not provided
        
        # Agent for analysis tasks (uses planning model)
        self.analysis_agent = Agent(
            name="TheCriticAgent_Analysis",
            instruction=THE_CRITIC_ANALYSIS_PROMPT,
            server_names=self.server_names
        )
        
        # Agent for code generation tasks (uses implementation model)
        self.coding_agent = Agent(
            name="TheCriticAgent_Coding",
            instruction=THE_CRITIC_CODING_PROMPT,
            server_names=self.server_names
        )
        
        # Log system prompts if logger is available
        if self.dialogue_logger:
            self.dialogue_logger.log_system_prompt("TheCritic_Analysis", THE_CRITIC_ANALYSIS_PROMPT)
            self.dialogue_logger.log_system_prompt("TheCritic_Coding", THE_CRITIC_CODING_PROMPT)
    
    async def generate_verification_tests(
        self,
        paper_path: str,
        game_model: Dict[str, Any],
        output_path: str = None,
        force_pdf_model: str = None
    ) -> str:
        """
        Generate verification test file
        
        Supports both markdown (.md) and PDF (.pdf) formats.
        For PDFs with mathematical notation, uses models with native PDF support.
        
        Args:
            paper_path: Path to paper file (.md or .pdf)
            game_model: Game model from The Theorist
            output_path: Optional path to save test file
            force_pdf_model: Force specific model for PDF processing
        
        Returns:
            test_code: Complete Python test file as string
        """
        paper_path = Path(paper_path)
        
        if not paper_path.exists():
            raise FileNotFoundError(f"Paper file not found: {paper_path}")
        
        # Check if input is PDF
        is_pdf = PDFProcessor.is_pdf(paper_path)
        
        if is_pdf:
            print(f"📄 Processing PDF for test generation: {paper_path.name}")
            return await self._generate_from_pdf(
                paper_path,
                game_model,
                output_path,
                force_pdf_model
            )
        else:
            print(f"📝 Processing markdown for test generation: {paper_path.name}")
            return await self._generate_from_markdown(
                paper_path,
                game_model,
                output_path
            )
    
    async def _generate_from_markdown(
        self,
        paper_path: Path,
        game_model: Dict[str, Any],
        output_path: str = None
    ) -> str:
        """
        Generate tests from markdown file using MCP filesystem tools.
        
        This is a two-phase process:
        1. Analysis phase (planning_model): Extract propositions from paper
        2. Coding phase (implementation_model): Generate Python test code
        """
        game_model_str = self._format_game_model(game_model)
        
        # Phase 1: Analysis - Extract propositions using planning_model
        print("   📖 Phase 1: Extracting propositions (planning model)...")
        analysis_prompt = f"""Analyze this paper and extract all theoretical results.

Paper location: {paper_path}

Game Model:
{game_model_str}

Tasks:
1. Read the paper and identify ALL Propositions, Lemmas, Corollaries, and Theorems
2. For each theoretical result, extract:
   - The exact statement
   - Key variables and conditions
   - Expected outcomes or predictions
3. Return a structured JSON list of propositions

Return the extracted propositions as a JSON array with format:
[{{"type": "Proposition", "number": "1", "statement": "...", "conditions": [...], "predictions": [...]}}]"""
        
        async with self.analysis_agent:
            llm = await self.analysis_agent.attach_llm(self.planning_factory)
            
            params = RequestParams(
                model=self.planning_model,
                maxTokens=16000,  # Increased to avoid truncation of proposition extraction
                temperature=0.2,
            )
            
            analysis_result = await llm.generate_str(
                message=analysis_prompt,
                request_params=params
            )
            
            # Log the analysis LLM call
            if self.dialogue_logger:
                self.dialogue_logger.log_llm_call(
                    agent_name="TheCritic",
                    phase="proposition_extraction_markdown",
                    prompt=analysis_prompt,
                    response=analysis_result or "",
                    model=self.planning_model or "",
                    request_params={
                        "maxTokens": 16000,
                        "temperature": params.temperature
                    },
                    extra_context={"paper_path": str(paper_path)}
                )
        
        # Phase 2: Coding - Generate test code using implementation_model
        print("   💻 Phase 2: Generating test code (implementation model)...")
        coding_prompt = f"""Generate Python verification tests based on extracted propositions.

Game Model:
{game_model_str}

Extracted Propositions and Theoretical Results:
{analysis_result}

Generate a complete test_verification.py file that:
1. Creates a Python unittest for EACH proposition/lemma/theorem
2. Tests should verify LLM agents at Temperature=0 reproduce the theoretical results
3. Include appropriate statistical tests for stochastic outcomes
4. Include clear docstrings with the exact proposition statement
5. Include all necessary imports (unittest, numpy, scipy.stats, etc.)

Return ONLY the complete Python test file code."""
        
        async with self.coding_agent:
            llm = await self.coding_agent.attach_llm(self.implementation_factory)
            
            params = RequestParams(
                model=self.implementation_model,
                maxTokens=16000,  # Increased to avoid truncation of generated test code
                temperature=0.2,
            )
            
            result = await llm.generate_str(
                message=coding_prompt,
                request_params=params
            )
            
            # Log the coding LLM call
            if self.dialogue_logger:
                self.dialogue_logger.log_llm_call(
                    agent_name="TheCritic",
                    phase="test_code_generation_markdown",
                    prompt=coding_prompt,
                    response=result or "",
                    model=self.implementation_model or "",
                    request_params={
                        "maxTokens": 16000,
                        "temperature": params.temperature
                    },
                    extra_context={"paper_path": str(paper_path)}
                )
        
        # Extract code
        test_code = self._extract_python_code(result)
        
        # Save if output path specified
        if output_path:
            with open(output_path, 'w') as f:
                f.write(test_code)
            print(f"   ✅ Verification tests saved to {output_path}")
        
        return test_code
    
    async def _generate_from_pdf(
        self,
        paper_path: Path,
        game_model: Dict[str, Any],
        output_path: str = None,
        force_model: str = None
    ) -> str:
        """
        Generate tests from PDF using LLM with native PDF support.
        
        This is a two-phase process:
        1. Analysis phase (planning_model): Extract propositions from PDF
        2. Coding phase (implementation_model): Generate Python test code
        """
        from utils.llm_utils import get_api_keys, load_api_config, get_default_models
        import httpx
        
        # Prepare PDF
        pdf_data = PDFProcessor.prepare_pdf_for_llm(paper_path, max_size_mb=20.0)
        print(f"   PDF size: {pdf_data['size_mb']:.2f} MB")
        
        game_model_str = self._format_game_model(game_model)
        
        # Get API configuration
        api_config = load_api_config()
        openrouter_config = api_config.get("openrouter", {})
        api_key = openrouter_config.get("api_key", "")
        
        if not api_key:
            raise ValueError("OpenRouter API key not found")
        
        base_url = openrouter_config.get("base_url", "https://openrouter.ai/api/v1")
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
        
        if "site_url" in openrouter_config:
            headers["HTTP-Referer"] = openrouter_config["site_url"]
        if "app_name" in openrouter_config:
            headers["X-Title"] = openrouter_config["app_name"]
        
        models = get_default_models()
        
        # ============================================================
        # Phase 1: Analysis - Extract propositions using PLANNING model
        # ============================================================
        print("   📖 Phase 1: Extracting propositions from PDF (planning model)...")
        
        # Select planning model (must support PDF)
        if force_model:
            planning_model = force_model
        else:
            planning_model = models.get("openrouter_planning", PDFProcessor.get_recommended_pdf_model())
            if not PDFProcessor.check_model_supports_pdf(planning_model):
                planning_model = PDFProcessor.get_recommended_pdf_model()
        
        print(f"      Using planning model: {planning_model}")
        
        analysis_prompt = f"""Analyze this research paper (PDF attached) and extract all theoretical results.

The paper contains mathematical propositions, lemmas, and corollaries with complex notation.

Game Model (already extracted):
{game_model_str}

Tasks:
1. Read the PDF and identify ALL Propositions, Lemmas, Corollaries, and Theorems
2. For EACH theoretical result, extract:
   - The exact statement (preserve mathematical notation)
   - Key variables and conditions
   - Expected outcomes or predictions
   - The section/page where it appears

Return a structured JSON array of propositions:
[{{"type": "Proposition", "number": "1", "statement": "...", "conditions": [...], "predictions": [...], "section": "..."}}]"""
        
        analysis_message = {
            "role": "user",
            "content": [
                {"type": "text", "text": analysis_prompt},
                {
                    "type": "inline_data",
                    "inline_data": {
                        "mime_type": "application/pdf",
                        "data": pdf_data['data']
                    }
                }
            ]
        }
        
        analysis_request = {
            "model": planning_model,
            "messages": [
                {"role": "system", "content": THE_CRITIC_ANALYSIS_PROMPT},
                analysis_message
            ],
            "max_tokens": 16000,  # Increased to avoid truncation of proposition extraction
            "temperature": 0.2,
        }
        
        async with httpx.AsyncClient(timeout=300.0) as client:
            response = await client.post(
                f"{base_url}/chat/completions",
                headers=headers,
                json=analysis_request
            )
            
            if response.status_code != 200:
                raise ValueError(f"OpenRouter API error (analysis phase): {response.status_code}\n{response.text}")
            
            result = response.json()
        
        try:
            analysis_result = result["choices"][0]["message"]["content"]
        except (KeyError, IndexError) as e:
            raise ValueError(f"Unexpected API response (analysis phase): {e}")
        
        # Log the analysis LLM call
        if self.dialogue_logger:
            self.dialogue_logger.log_llm_call(
                agent_name="TheCritic",
                phase="proposition_extraction_pdf",
                prompt=analysis_prompt,
                response=analysis_result or "",
                model=planning_model,
                request_params={
                    "max_tokens": 16000,
                    "temperature": 0.2
                },
                extra_context={
                    "paper_path": str(paper_path),
                    "pdf_size_mb": pdf_data['size_mb']
                }
            )
        
        # ============================================================
        # Phase 2: Coding - Generate test code using IMPLEMENTATION model
        # ============================================================
        print("   💻 Phase 2: Generating test code (implementation model)...")
        
        # Select implementation model
        implementation_model = models.get("openrouter_implementation", models.get("openrouter"))
        print(f"      Using implementation model: {implementation_model}")
        
        coding_prompt = f"""Generate Python verification tests based on extracted propositions.

Game Model:
{game_model_str}

Extracted Propositions and Theoretical Results:
{analysis_result}

Generate a COMPLETE test_verification.py file that:
1. Creates a Python unittest for EACH proposition/lemma/theorem
2. Tests should verify that LLM agents at Temperature=0 can reproduce the theoretical predictions
3. Include clear docstrings with the exact proposition statement from the paper
4. Use appropriate statistical tests for stochastic outcomes (e.g., t-tests for welfare comparisons)
5. Reference the game model structure provided above
6. Include all necessary imports (unittest, numpy, scipy.stats, etc.)
7. Include setUp method to initialize environment and agents
8. Include helper methods as needed

The test file should be ready to run with: python -m unittest test_verification.py

Return ONLY the complete Python test file code."""
        
        coding_request = {
            "model": implementation_model,
            "messages": [
                {"role": "system", "content": THE_CRITIC_CODING_PROMPT},
                {"role": "user", "content": coding_prompt}
            ],
            "max_tokens": 16000,  # Increased to avoid truncation of generated test code
            "temperature": 0.2,
        }
        
        async with httpx.AsyncClient(timeout=300.0) as client:
            response = await client.post(
                f"{base_url}/chat/completions",
                headers=headers,
                json=coding_request
            )
            
            if response.status_code != 200:
                raise ValueError(f"OpenRouter API error (coding phase): {response.status_code}\n{response.text}")
            
            result = response.json()
        
        try:
            content = result["choices"][0]["message"]["content"]
        except (KeyError, IndexError) as e:
            raise ValueError(f"Unexpected API response (coding phase): {e}")
        
        # Log the coding LLM call
        if self.dialogue_logger:
            self.dialogue_logger.log_llm_call(
                agent_name="TheCritic",
                phase="test_code_generation_pdf",
                prompt=coding_prompt,
                response=content or "",
                model=implementation_model,
                request_params={
                    "max_tokens": 16000,
                    "temperature": 0.2
                },
                extra_context={
                    "paper_path": str(paper_path),
                    "pdf_size_mb": pdf_data['size_mb']
                }
            )
        
        # Extract code
        test_code = self._extract_python_code(content)
        
        # Save if output path specified
        if output_path:
            with open(output_path, 'w') as f:
                f.write(test_code)
            print(f"   ✅ Verification tests saved to {output_path}")
        
        return test_code
    
    def _format_game_model(self, game_model: Dict[str, Any]) -> str:
        """Format game model for prompt context"""
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
