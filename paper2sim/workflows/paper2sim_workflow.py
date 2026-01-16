"""
Paper2Sim Workflow - Complete Pipeline

Orchestrates all phases to convert a paper into a working simulation.

Supports both markdown (.md) and PDF (.pdf) input formats.
For PDF papers with complex mathematical formulas (common in OR/OM/MS fields),
uses LLM models with native PDF support (e.g., Gemini via OpenRouter) to
preserve mathematical notation and formulas.
"""

import os
import asyncio
from typing import Dict, Any, Optional
from pathlib import Path

# Import agents
from paper2sim.agents.theorist import TheTheoristAgent
from paper2sim.agents.critic import TheCriticAgent
from paper2sim.agents.architect import TheArchitectAgent
from paper2sim.agents.engineer import TheEngineerAgent
from paper2sim.agents.qa_specialist import TheQASpecialistAgent


class Paper2SimWorkflow:
    """
    Complete Paper-to-Simulation workflow
    
    Phases:
    1. Deconstruction: Extract game model (Theorist) + Generate tests (Critic)
    2. Architecture: Design code structure (Architect) + Implement code (Engineer)
    3. Verification: Calibrate agents (QA Specialist)
    4. Emergence: Add advanced features (optional)
    
    Model Assignment:
    - Planning model: Used for analysis tasks (Theorist, Architect, Critic analysis, QA diagnosis)
    - Implementation model: Used for coding tasks (Engineer, Critic test generation, QA fixes)
    """
    
    def __init__(
        self, 
        llm_factory=None,
        planning_factory=None,
        implementation_factory=None,
        planning_model=None,
        implementation_model=None,
        output_base_dir: str = "./paper2sim_output"
    ):
        """
        Initialize Paper2Sim workflow
        
        Args:
            llm_factory: Legacy single LLM factory (used if planning/implementation not specified)
            planning_factory: LLM factory for analysis/planning tasks
            implementation_factory: LLM factory for code generation tasks
            planning_model: Specific model name for planning tasks (e.g., "google/gemini-3-pro-preview")
            implementation_model: Specific model name for coding tasks (e.g., "anthropic/claude-sonnet-4.5")
            output_base_dir: Base directory for output files
        """
        # Support both legacy single-factory and new dual-factory modes
        if planning_factory is None:
            planning_factory = llm_factory
        if implementation_factory is None:
            implementation_factory = llm_factory
            
        self.planning_factory = planning_factory
        self.implementation_factory = implementation_factory
        self.planning_model = planning_model
        self.implementation_model = implementation_model
        self.output_base_dir = output_base_dir
        
        # Initialize agents with appropriate factories AND model names
        # Theorist: Analysis only → planning_factory + planning_model
        self.theorist = TheTheoristAgent(
            planning_factory, 
            server_names=["filesystem", "brave"],
            model_name=planning_model
        )
        
        # Critic: Both analysis and coding → both factories + model names
        self.critic = TheCriticAgent(
            planning_factory=planning_factory,
            implementation_factory=implementation_factory,
            server_names=["filesystem"],
            planning_model=planning_model,
            implementation_model=implementation_model
        )
        
        # Architect: Analysis only → planning_factory
        self.architect = TheArchitectAgent(
            planning_factory, 
            server_names=[]
        )
        
        # Engineer: Coding only → implementation_factory
        self.engineer = TheEngineerAgent(
            implementation_factory, 
            server_names=["code-implementation"]
        )
        
        # QA Specialist: Both diagnosis and fixes → both factories
        self.qa_specialist = TheQASpecialistAgent(
            planning_factory=planning_factory,
            implementation_factory=implementation_factory,
            server_names=[]
        )
    
    async def run_full_pipeline(
        self,
        paper_path: str,
        project_name: str = None,
        enable_phase4: bool = False
    ) -> Dict[str, Any]:
        """
        Run complete Paper2Sim pipeline
        
        Args:
            paper_path: Path to research paper (.md or .pdf)
                       PDF support enables direct processing of papers with
                       complex mathematical notation using models like Gemini
            project_name: Name for output directory
            enable_phase4: Enable advanced emergence features
        
        Returns:
            results: Complete workflow results
        """
        # Setup output directory
        if project_name is None:
            project_name = Path(paper_path).stem
        
        output_dir = os.path.join(self.output_base_dir, project_name)
        os.makedirs(output_dir, exist_ok=True)
        
        print(f"🧬 Paper2Sim Pipeline Started")
        print(f"📄 Paper: {paper_path}")
        print(f"📁 Output: {output_dir}")
        print("=" * 70)
        
        results = {}
        
        # ============================================================
        # Phase 1: Deconstruction (The Theorist + The Critic)
        # ============================================================
        print("\n📊 Phase 1: Deconstruction")
        print("-" * 70)
        
        # Step 1.1: Extract game model
        print("Running The Theorist...")
        game_model = await self.theorist.extract_game_model(paper_path)
        
        # Save game model
        game_model_path = os.path.join(output_dir, "game_model.json")
        import json
        with open(game_model_path, 'w') as f:
            json.dump(game_model, f, indent=2)
        print(f"✓ Game model saved to {game_model_path}")
        
        # Validate
        if not self.theorist.validate_game_model(game_model):
            print("⚠ Warning: Game model may be incomplete")
        
        results['game_model'] = game_model
        results['game_model_path'] = game_model_path
        
        # Step 1.2: Generate verification tests
        print("\nRunning The Critic...")
        test_path = os.path.join(output_dir, "test_verification.py")
        test_code = await self.critic.generate_verification_tests(
            paper_path, game_model, test_path
        )
        print(f"✓ Verification tests saved to {test_path}")
        
        results['verification_tests'] = test_code
        results['test_path'] = test_path
        
        # ============================================================
        # Phase 2: Architecture & Coding (The Architect + The Engineer)
        # ============================================================
        print("\n🏗️ Phase 2: Architecture & Coding")
        print("-" * 70)
        
        # Step 2.1: Design architecture
        print("Running The Architect...")
        architecture = await self.architect.design_architecture(game_model, test_code)
        
        # Save architecture
        arch_path = os.path.join(output_dir, "architecture.json")
        with open(arch_path, 'w') as f:
            json.dump(architecture, f, indent=2)
        print(f"✓ Architecture saved to {arch_path}")
        
        # Validate
        if not self.architect.validate_architecture(architecture):
            print("⚠ Warning: Architecture may be incomplete")
        
        results['architecture'] = architecture
        results['architecture_path'] = arch_path
        
        # Step 2.2: Implement code
        print("\nRunning The Engineer...")
        simulation_dir = os.path.join(output_dir, "simulation")
        generated_files = await self.engineer.implement_simulation(
            architecture, game_model, test_code, simulation_dir
        )
        print(f"✓ Simulation code generated in {simulation_dir}")
        
        results['simulation_dir'] = simulation_dir
        results['generated_files'] = generated_files
        
        # ============================================================
        # Phase 3: Verification & Calibration (The QA Specialist)
        # ============================================================
        print("\n🔬 Phase 3: Verification & Calibration")
        print("-" * 70)
        
        print("Running The QA Specialist...")
        calibration_report = await self.qa_specialist.calibrate_agents(
            test_module_path=test_path,
            simulation_dir=simulation_dir,
            max_iterations=10
        )
        
        if calibration_report.is_calibrated:
            print("✅ Calibration successful - agents verified!")
        else:
            print(f"⚠ Calibration incomplete: {calibration_report.pass_rate:.1%} pass rate")
        
        results['calibration_report'] = calibration_report
        results['is_calibrated'] = calibration_report.is_calibrated
        
        # ============================================================
        # Phase 4: Advanced Emergence (Optional)
        # ============================================================
        if enable_phase4 and calibration_report.is_calibrated:
            print("\n🌟 Phase 4: Advanced Emergence")
            print("-" * 70)
            print("Note: Phase 4 features (memory, language, red teaming) can be added manually")
            print("Prompts available in paper2sim/prompts/phase4_prompts.py")
            # Phase 4 implementation would go here
        
        # ============================================================
        # Summary
        # ============================================================
        print("\n" + "=" * 70)
        print("✨ Paper2Sim Pipeline Complete")
        print("=" * 70)
        print(f"📁 Output directory: {output_dir}")
        print(f"🎮 Simulation code: {simulation_dir}")
        print(f"📊 Game model: {game_model_path}")
        print(f"🧪 Tests: {test_path}")
        print(f"✅ Calibrated: {results['is_calibrated']}")
        
        if results['is_calibrated']:
            print("\n🚀 Ready to run simulations!")
            print(f"   cd {simulation_dir}")
            print("   python main.py")
        else:
            print("\n⚠️ Calibration incomplete - manual fixes may be needed")
        
        return results
    
    async def run_phase1(self, paper_path: str, output_dir: str) -> Dict[str, Any]:
        """Run only Phase 1 (Deconstruction)"""
        game_model = await self.theorist.extract_game_model(paper_path)
        test_code = await self.critic.generate_verification_tests(
            paper_path, game_model
        )
        
        return {
            'game_model': game_model,
            'verification_tests': test_code
        }
    
    async def run_phase2(
        self,
        game_model: Dict[str, Any],
        verification_tests: str,
        output_dir: str
    ) -> Dict[str, Any]:
        """Run only Phase 2 (Architecture & Coding)"""
        architecture = await self.architect.design_architecture(
            game_model, verification_tests
        )
        generated_files = await self.engineer.implement_simulation(
            architecture, game_model, verification_tests, output_dir
        )
        
        return {
            'architecture': architecture,
            'generated_files': generated_files
        }
    
    async def run_phase3(
        self,
        test_module_path: str,
        simulation_dir: str
    ) -> Dict[str, Any]:
        """Run only Phase 3 (Verification & Calibration)"""
        calibration_report = await self.qa_specialist.calibrate_agents(
            test_module_path, simulation_dir
        )
        
        return {
            'calibration_report': calibration_report,
            'is_calibrated': calibration_report.is_calibrated
        }
