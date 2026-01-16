#!/usr/bin/env python3
"""
Paper2Sim CLI - Main Entry Point

Convert research papers to working simulations.
"""

import argparse
import asyncio
import sys
from pathlib import Path

from paper2sim.workflows.paper2sim_workflow import Paper2SimWorkflow
from utils.llm_utils import get_preferred_llm_class


def print_banner():
    """Display startup banner"""
    banner = """
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║    📄 Paper2Sim - Hybrid OR/LLM Simulation Engine           ║
║                                                              ║
║    Convert Research Papers → Working Simulations             ║
║    Environment as Law (Math) | Agent as Brain (LLM)         ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
"""
    print(banner)


async def run_pipeline(args):
    """Run the Paper2Sim pipeline"""
    # Validate paper path
    paper_path = Path(args.paper)
    if not paper_path.exists():
        print(f"❌ Error: Paper not found: {paper_path}")
        sys.exit(1)
    
    if not paper_path.suffix == '.md':
        print(f"❌ Error: Paper must be in markdown format (.md)")
        sys.exit(1)
    
    # Get LLM factory
    llm_factory = get_preferred_llm_class()
    
    # Initialize workflow
    workflow = Paper2SimWorkflow(
        llm_factory=llm_factory,
        output_base_dir=args.output or "./paper2sim_output"
    )
    
    # Run pipeline
    try:
        results = await workflow.run_full_pipeline(
            paper_path=str(paper_path),
            project_name=args.name,
            enable_phase4=args.phase4
        )
        
        # Success
        if results['is_calibrated']:
            print("\n✅ Pipeline completed successfully!")
            return 0
        else:
            print("\n⚠️ Pipeline completed with warnings (calibration incomplete)")
            return 1
            
    except Exception as e:
        print(f"\n❌ Pipeline failed: {e}")
        import traceback
        traceback.print_exc()
        return 1


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Paper2Sim: Convert research papers to simulations",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic usage
  python -m paper2sim.main --paper papers/physician_testing.md
  
  # Specify output directory and project name
  python -m paper2sim.main --paper papers/signaling_game.md \\
      --output ./my_sims --name signaling_sim
  
  # Enable Phase 4 (advanced emergence features)
  python -m paper2sim.main --paper papers/mechanism_design.md --phase4
  
  # Run specific phase only
  python -m paper2sim.main --paper papers/game.md --phase 1  # Deconstruction only

For more information, see: https://github.com/yourusername/paper2sim
        """
    )
    
    parser.add_argument(
        '--paper',
        type=str,
        required=True,
        help='Path to research paper (markdown format)'
    )
    
    parser.add_argument(
        '--output',
        type=str,
        default='./paper2sim_output',
        help='Output directory for generated simulations (default: ./paper2sim_output)'
    )
    
    parser.add_argument(
        '--name',
        type=str,
        default=None,
        help='Project name (default: derived from paper filename)'
    )
    
    parser.add_argument(
        '--phase4',
        action='store_true',
        help='Enable Phase 4: Advanced emergence features (memory, language, red teaming)'
    )
    
    parser.add_argument(
        '--phase',
        type=int,
        choices=[1, 2, 3],
        default=None,
        help='Run specific phase only (1=Deconstruction, 2=Architecture, 3=Verification)'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version='Paper2Sim v0.1.0'
    )
    
    args = parser.parse_args()
    
    # Print banner
    print_banner()
    
    # Run pipeline
    exit_code = asyncio.run(run_pipeline(args))
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
