"""
The Theorist Agent - Game Model Extraction

Extracts the game-theoretic structure <N, S, A, U> from research papers.
Supports both markdown and PDF input formats.
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional
from mcp_agent.agents.agent import Agent
from mcp_agent.workflows.llm.augmented_llm import RequestParams
from paper2sim.prompts.phase1_prompts import THE_THEORIST_PROMPT
from tools.pdf_processor import PDFProcessor

# Import logger with fallback
try:
    from paper2sim.utils.llm_dialogue_logger import LLMDialogueLogger, get_shared_logger
except ImportError:
    LLMDialogueLogger = None
    def get_shared_logger():
        return None


class TheTheoristAgent:
    """
    Extracts structured game models from research papers
    
    This agent identifies:
    - Players (N)
    - States (S)
    - Actions (A)
    - Utilities (U)
    And converts them to a structured JSON format.
    
    Model Assignment: Uses PLANNING model (analysis task, no coding)
    """
    
    def __init__(self, llm_factory=None, server_names=None, model_name=None, dialogue_logger=None):
        """
        Initialize The Theorist
        
        Args:
            llm_factory: LLM factory for agent creation (should be planning_factory)
            server_names: MCP servers to use (typically filesystem + search)
            model_name: Specific model name to use (e.g., "google/gemini-3-pro-preview")
            dialogue_logger: Optional LLMDialogueLogger for recording LLM inputs/outputs
        
        Note: This agent performs analysis tasks only, no code generation.
              Should use the planning_model for best results.
        """
        self.llm_factory = llm_factory  # Planning model for analysis
        self.server_names = server_names or ["filesystem"]  # Removed brave, only use filesystem
        self.model_name = model_name  # Specific model to use
        self.dialogue_logger = dialogue_logger or get_shared_logger()  # Use shared logger if not provided
        
        # Create MCP agent
        self.agent = Agent(
            name="TheTheoristAgent",
            instruction=THE_THEORIST_PROMPT,
            server_names=self.server_names
        )
        
        # Log system prompt if logger is available
        if self.dialogue_logger:
            self.dialogue_logger.log_system_prompt("TheTheorist", THE_THEORIST_PROMPT)
    
    async def extract_game_model(
        self,
        paper_path: str,
        additional_context: str = None,
        force_pdf_model: str = None
    ) -> Dict[str, Any]:
        """
        Extract game-theoretic model from paper
        
        Supports both markdown (.md) and PDF (.md) formats.
        For PDFs, uses LLM models with native PDF support (e.g., Gemini)
        via OpenRouter to preserve mathematical formulas and notation.
        
        Args:
            paper_path: Path to paper file (.md or .pdf)
            additional_context: Optional additional instructions
            force_pdf_model: Force specific model for PDF processing
                           (e.g., "google/gemini-2.0-flash-exp")
        
        Returns:
            game_model: Structured JSON with game components
        """
        # Debug: Check API configuration
        from utils.llm_utils import get_api_keys
        keys = get_api_keys()
        print(f"🔍 DEBUG: OpenRouter API key present: {bool(keys.get('openrouter'))}")
        if keys.get('openrouter'):
            print(f"🔍 DEBUG: API key starts with: {keys['openrouter'][:15]}...")
        
        paper_path = Path(paper_path)
        
        if not paper_path.exists():
            raise FileNotFoundError(f"Paper file not found: {paper_path}")
        
        # Check if input is PDF
        is_pdf = PDFProcessor.is_pdf(paper_path)
        
        if is_pdf:
            print(f"📄 Detected PDF input: {paper_path.name}")
            print("   Using LLM with native PDF support to preserve mathematical notation")
            return await self._extract_from_pdf(
                paper_path, 
                additional_context,
                force_pdf_model
            )
        else:
            print(f"📝 Detected markdown input: {paper_path.name}")
            return await self._extract_from_markdown(
                paper_path,
                additional_context
            )
    
    async def _extract_from_markdown(
        self,
        paper_path: Path,
        additional_context: str = None
    ) -> Dict[str, Any]:
        """
        Extract game model from markdown file using MCP filesystem tools.
        
        Args:
            paper_path: Path to markdown file
            additional_context: Optional additional context
            
        Returns:
            game_model: Extracted game model
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
        
        # Execute extraction using MCP agent with filesystem tools
        async with self.agent:
            llm = await self.agent.attach_llm(self.llm_factory)
            
            # Debug: Print LLM configuration
            print(f"🔍 DEBUG: LLM class: {llm.__class__.__name__}")
            print(f"🔍 DEBUG: LLM attributes: {dir(llm)[:10]}...")  # First 10 attributes
            
            # Check various possible model attribute names
            for attr in ['model', 'default_model', '_model', 'model_name']:
                if hasattr(llm, attr):
                    print(f"🔍 DEBUG: {attr}: {getattr(llm, attr)}")
            
            # Check client configuration
            if hasattr(llm, 'client'):
                print(f"🔍 DEBUG: Has client: True")
                if hasattr(llm.client, 'base_url'):
                    print(f"🔍 DEBUG: Base URL: {llm.client.base_url}")
                if hasattr(llm.client, 'api_key'):
                    print(f"🔍 DEBUG: API key configured: {bool(llm.client.api_key)}")
            else:
                print(f"🔍 DEBUG: Has client: False")
            
            params = RequestParams(
                model=self.model_name,
                maxTokens=8000,
                temperature=0.2,
            )
            
            print(f"🔍 DEBUG: Request params: model={params.model}, maxTokens={params.maxTokens}, temp={params.temperature}")
            print(f"🔍 DEBUG: Prompt length: {len(prompt)} characters")
            
            try:
                result = await llm.generate_str(
                    message=prompt,
                    request_params=params
                )
                print(f"🔍 DEBUG: Result length: {len(result) if result else 0} characters")
                if result:
                    print(f"🔍 DEBUG: First 200 chars: {result[:200]}")
                else:
                    print(f"⚠️ DEBUG: Result is empty or None!")
                
                # Log the LLM call
                if self.dialogue_logger:
                    self.dialogue_logger.log_llm_call(
                        agent_name="TheTheorist",
                        phase="game_model_extraction_markdown",
                        prompt=prompt,
                        response=result or "",
                        model=self.model_name or "",
                        request_params={
                            "maxTokens": params.maxTokens,
                            "temperature": params.temperature
                        },
                        extra_context={"paper_path": str(paper_path)}
                    )
            except Exception as e:
                print(f"❌ DEBUG: Exception during generate_str: {type(e).__name__}: {e}")
                import traceback
                traceback.print_exc()
                raise
        
        # Parse result
        try:
            game_model = json.loads(self._extract_json(result))
            return game_model
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse game model JSON: {e}\nRaw output: {result}")
    
    async def _extract_from_pdf(
        self,
        paper_path: Path,
        additional_context: str = None,
        force_model: str = None
    ) -> Dict[str, Any]:
        """
        Extract game model from PDF using LLM with native PDF support.
        
        This method directly sends the PDF to models like Gemini that can
        process PDF content natively, preserving mathematical formulas.
        
        Args:
            paper_path: Path to PDF file
            additional_context: Optional additional context
            force_model: Force specific model (e.g., "google/gemini-2.0-flash-exp")
            
        Returns:
            game_model: Extracted game model
        """
        from utils.llm_utils import get_api_keys, load_api_config
        
        # Prepare PDF for API
        try:
            pdf_data = PDFProcessor.prepare_pdf_for_llm(paper_path, max_size_mb=20.0)
            print(f"   PDF size: {pdf_data['size_mb']:.2f} MB")
        except ValueError as e:
            raise ValueError(f"PDF file too large or invalid: {e}")
        
        # Build extraction prompt
        prompt = f"""Extract the game-theoretic model from this research paper (PDF attached).

This paper is from the Operations Research (OR), Operations Management (OM), or Management Science (MS) field, 
and contains extensive mathematical formulas and notation that must be preserved accurately.

{additional_context if additional_context else ""}

Follow the extraction protocol to identify:
1. Players (N) - All agents/decision-makers in the model
2. State variables (S) - Complete state space with mathematical definitions
3. Action spaces (A) - Available actions for each player with constraints
4. Utility functions (U) - Exact mathematical expressions for each player's payoff
5. Game timing and information structure - Sequence of moves and information sets
6. Equilibrium concept - Type of equilibrium (Perfect Bayesian, Nash, etc.)
7. Parameters - All model parameters with their meanings and typical values

CRITICAL REQUIREMENTS:
- Copy ALL mathematical formulas EXACTLY as they appear in the paper
- Preserve notation: Greek letters, subscripts, superscripts, special symbols
- Include equation numbers and section references
- Extract transition dynamics and Bayesian updating rules with full mathematical detail
- Do NOT simplify or approximate formulas

Return a complete JSON following this schema:
{json.dumps({
    "paper_title": "string",
    "game_type": "signaling|screening|mechanism_design|repeated|other",
    "players": {"N": ["player1", "player2"], "descriptions": {}},
    "state_variables": [{"name": "string", "type": "string", "range": "string", "description": "string", "initial_value": "string"}],
    "actions": {"player1": [{"name": "string", "description": "string", "cost": "string", "constraints": "string"}]},
    "transition_logic": [{"state_var": "string", "trigger": "string", "formula_latex": "string", "formula_python": "string", "description": "string"}],
    "payoff_functions": {"player1": {"formula_latex": "string", "formula_python": "string", "components": []}},
    "game_timeline": [{"stage": 1, "description": "string", "players_acting": [], "information": "string", "actions": []}],
    "equilibrium_concept": {"type": "string", "description": "string"},
    "parameters": [{"symbol": "string", "name": "string", "typical_value": "string", "source": "string"}]
}, indent=2)}"""
        
        # Get API configuration
        api_config = load_api_config()
        openrouter_config = api_config.get("openrouter", {})
        api_key = openrouter_config.get("api_key", "")
        
        if not api_key:
            raise ValueError(
                "OpenRouter API key not found. Please set OPENROUTER_API_KEY "
                "environment variable or add to mcp_agent.secrets.yaml"
            )
        
        # Select model
        if force_model:
            model = force_model
        else:
            # Use recommended PDF model or configured default
            from utils.llm_utils import get_default_models
            models = get_default_models()
            model = models.get("openrouter_planning", PDFProcessor.get_recommended_pdf_model())
            
            # Verify model supports PDF
            if not PDFProcessor.check_model_supports_pdf(model):
                print(f"⚠️  Model {model} may not support PDF input, switching to recommended model")
                model = PDFProcessor.get_recommended_pdf_model()
        
        print(f"   Using model: {model}")
        
        # Make API call with PDF
        import httpx
        
        base_url = openrouter_config.get("base_url", "https://openrouter.ai/api/v1")
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
        
        # Optional: Add site info for OpenRouter rankings
        if "site_url" in openrouter_config:
            headers["HTTP-Referer"] = openrouter_config["site_url"]
        if "app_name" in openrouter_config:
            headers["X-Title"] = openrouter_config["app_name"]
        
        # Format message with PDF
        message = {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": prompt
                },
                {
                    "type": "inline_data",
                    "inline_data": {
                        "mime_type": "application/pdf",
                        "data": pdf_data['data']
                    }
                }
            ]
        }
        
        request_body = {
            "model": model,
            "messages": [
                {
                    "role": "system",
                    "content": THE_THEORIST_PROMPT
                },
                message
            ],
            "max_tokens": 8000,
            "temperature": 0.2,
        }
        
        print("   Sending PDF to LLM for analysis...")
        
        async with httpx.AsyncClient(timeout=300.0) as client:
            response = await client.post(
                f"{base_url}/chat/completions",
                headers=headers,
                json=request_body
            )
            
            if response.status_code != 200:
                raise ValueError(
                    f"OpenRouter API error: {response.status_code}\n{response.text}"
                )
            
            result = response.json()
        
        # Extract content from response
        try:
            content = result["choices"][0]["message"]["content"]
        except (KeyError, IndexError) as e:
            raise ValueError(f"Unexpected API response format: {e}\n{result}")
        
        # Log the LLM call
        if self.dialogue_logger:
            self.dialogue_logger.log_llm_call(
                agent_name="TheTheorist",
                phase="game_model_extraction_pdf",
                prompt=prompt,
                response=content or "",
                model=model,
                request_params={
                    "max_tokens": 8000,
                    "temperature": 0.2
                },
                extra_context={
                    "paper_path": str(paper_path),
                    "pdf_size_mb": pdf_data['size_mb']
                }
            )
        
        # Parse JSON result
        try:
            game_model = json.loads(self._extract_json(content))
            print("   ✅ Successfully extracted game model from PDF")
            return game_model
        except json.JSONDecodeError as e:
            raise ValueError(
                f"Failed to parse game model JSON: {e}\n"
                f"Raw output: {content[:500]}..."
            )
    
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
