"""
Example Usage of Paper2Sim

This example shows how to use the Paper2Sim workflow to convert
a research paper into a working simulation.
"""

import asyncio
from pathlib import Path
from paper2sim.workflows.paper2sim_workflow import Paper2SimWorkflow
from utils.llm_utils import get_preferred_llm_class


async def main():
    """Example pipeline run"""
    
    print("=" * 70)
    print("Paper2Sim Example Usage")
    print("=" * 70)
    
    # Example paper path (you'll need to provide your own paper)
    paper_path = "papers/example_paper.md"
    
    # Check if paper exists
    if not Path(paper_path).exists():
        print(f"\n⚠️ Example paper not found: {paper_path}")
        print("\nTo use this example:")
        print("1. Place a research paper (in markdown) at papers/example_paper.md")
        print("2. Or modify paper_path to point to your paper")
        print("\nPaper should contain:")
        print("- Game-theoretic model (players, states, actions, utilities)")
        print("- Propositions/Lemmas/Corollaries")
        print("- Mathematical formulas and equilibrium concepts")
        return
    
    # Initialize workflow with LLM factory
    llm_factory = get_preferred_llm_class()
    
    workflow = Paper2SimWorkflow(
        llm_factory=llm_factory,
        output_base_dir="./paper2sim_examples"
    )
    
    # Run complete pipeline
    print("\n🚀 Running Paper2Sim pipeline...")
    print("-" * 70)
    
    try:
        results = await workflow.run_full_pipeline(
            paper_path=paper_path,
            project_name="example_simulation",
            enable_phase4=False  # Start without Phase 4
        )
        
        print("\n" + "=" * 70)
        print("📊 Results Summary")
        print("=" * 70)
        
        print(f"\n✓ Game Model: {results['game_model_path']}")
        print(f"✓ Verification Tests: {results['test_path']}")
        print(f"✓ Architecture: {results['architecture_path']}")
        print(f"✓ Simulation Code: {results['simulation_dir']}")
        
        if results['is_calibrated']:
            print(f"\n✅ Status: CALIBRATED")
            print("\nYou can now:")
            print(f"1. Run simulations: cd {results['simulation_dir']} && python main.py")
            print("2. Modify parameters in config.py")
            print("3. Enable Phase 4 features (memory, language, red teaming)")
        else:
            print(f"\n⚠️ Status: NOT CALIBRATED")
            print("Some verification tests failed. Review calibration report:")
            print(f"{results['simulation_dir']}/calibration_report.json")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
