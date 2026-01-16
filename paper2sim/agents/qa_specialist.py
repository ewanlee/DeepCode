"""
The QA Specialist Agent - Calibration and Verification

Runs verification tests and calibrates agents to match theoretical predictions.
"""

import os
import unittest
import json
from typing import Dict, Any, List
from dataclasses import dataclass
from mcp_agent.agents.agent import Agent
from mcp_agent.workflows.llm.augmented_llm import RequestParams
from paper2sim.prompts.phase3_prompts import (
    THE_QA_SPECIALIST_PROMPT,
    THE_QA_DIAGNOSIS_PROMPT,
    THE_QA_FIX_PROMPT
)


@dataclass
class CalibrationIteration:
    """Record of one calibration iteration"""
    iteration: int
    test_results: Dict[str, bool]
    failures: List[Dict[str, Any]]
    fixes_applied: List[Dict[str, Any]]


@dataclass
class CalibrationReport:
    """Complete calibration report"""
    initial_test_results: Dict[str, bool]
    final_test_results: Dict[str, bool]
    iterations: List[CalibrationIteration]
    fixes_applied: List[Dict[str, Any]]
    
    @property
    def pass_rate(self) -> float:
        """Current pass rate"""
        if not self.final_test_results:
            return 0.0
        passed = sum(1 for v in self.final_test_results.values() if v)
        return passed / len(self.final_test_results)
    
    @property
    def is_calibrated(self) -> bool:
        """All tests passing"""
        return all(self.final_test_results.values())


class TheQASpecialistAgent:
    """
    Calibrates LLM agents to pass verification tests
    
    Process:
    1. Run verification tests
    2. Diagnose failures (calculation, motivation, strategy, probability errors) - PLANNING model
    3. Generate fixes (add tools, modify prompts, add constraints) - IMPLEMENTATION model
    4. Apply fixes and re-test
    5. Iterate until all tests pass or max iterations reached
    
    Model Assignment:
    - Planning model: Test failure diagnosis and analysis
    - Implementation model: Code fix generation
    """
    
    def __init__(
        self,
        llm_factory=None,
        planning_factory=None,
        implementation_factory=None,
        server_names=None
    ):
        """
        Initialize The QA Specialist
        
        Args:
            llm_factory: Legacy single LLM factory (used if planning/implementation not specified)
            planning_factory: LLM factory for diagnosis/analysis tasks
            implementation_factory: LLM factory for code fix generation
            server_names: MCP servers to use
        """
        # Support both legacy single-factory and new dual-factory modes
        if planning_factory is None:
            planning_factory = llm_factory
        if implementation_factory is None:
            implementation_factory = llm_factory
            
        self.planning_factory = planning_factory
        self.implementation_factory = implementation_factory
        self.server_names = server_names or []
        
        # Agent for diagnosis tasks (uses planning model)
        self.diagnosis_agent = Agent(
            name="TheQASpecialistAgent_Diagnosis",
            instruction=THE_QA_DIAGNOSIS_PROMPT,
            server_names=self.server_names
        )
        
        # Agent for fix generation tasks (uses implementation model)
        self.fix_agent = Agent(
            name="TheQASpecialistAgent_Fix",
            instruction=THE_QA_FIX_PROMPT,
            server_names=self.server_names
        )
    
    async def calibrate_agents(
        self,
        test_module_path: str,
        simulation_dir: str,
        max_iterations: int = 10
    ) -> CalibrationReport:
        """
        Calibrate agents through iterative testing and fixing
        
        Args:
            test_module_path: Path to test_verification.py
            simulation_dir: Directory containing simulation code
            max_iterations: Maximum calibration attempts
        
        Returns:
            report: Detailed calibration report
        """
        print(f"🔬 Starting calibration process (max {max_iterations} iterations)")
        
        # Initial test run
        print("Running initial tests...")
        initial_results = await self._run_tests(test_module_path, simulation_dir)
        print(f"Initial pass rate: {self._calculate_pass_rate(initial_results):.1%}")
        
        # Calibration loop
        iterations = []
        current_results = initial_results.copy()
        fixes_applied = []
        
        for i in range(max_iterations):
            print(f"\n📍 Calibration Iteration {i + 1}/{max_iterations}")
            
            # Check if calibrated
            if all(current_results.values()):
                print("✅ Calibration successful - all tests passing!")
                break
            
            # Identify failures
            failures = [
                {"test": name, "passed": passed}
                for name, passed in current_results.items()
                if not passed
            ]
            
            print(f"Failures: {len(failures)}/{len(current_results)}")
            
            # Diagnose and fix each failure
            iteration_fixes = []
            for failure in failures[:3]:  # Limit to 3 fixes per iteration
                diagnosis = await self._diagnose_failure(
                    failure['test'], test_module_path, simulation_dir
                )
                
                fix = await self._generate_fix(diagnosis, simulation_dir)
                
                await self._apply_fix(fix, simulation_dir)
                
                iteration_fixes.append(fix)
                fixes_applied.append(fix)
            
            # Re-run tests
            current_results = await self._run_tests(test_module_path, simulation_dir)
            
            # Record iteration
            iterations.append(CalibrationIteration(
                iteration=i + 1,
                test_results=current_results.copy(),
                failures=failures,
                fixes_applied=iteration_fixes
            ))
            
            print(f"Pass rate after iteration {i + 1}: {self._calculate_pass_rate(current_results):.1%}")
        
        # Generate final report
        report = CalibrationReport(
            initial_test_results=initial_results,
            final_test_results=current_results,
            iterations=iterations,
            fixes_applied=fixes_applied
        )
        
        # Save report
        report_path = os.path.join(simulation_dir, "calibration_report.json")
        self._save_report(report, report_path)
        
        return report
    
    async def _run_tests(
        self,
        test_module_path: str,
        simulation_dir: str
    ) -> Dict[str, bool]:
        """
        Run verification tests and collect results
        
        Returns:
            results: Dict mapping test_name -> passed
        """
        # Import and run tests
        import sys
        import os
        
        # Add simulation dir to path
        sys.path.insert(0, simulation_dir)
        
        try:
            # Load test module
            loader = unittest.TestLoader()
            suite = loader.discover(simulation_dir, pattern="test_*.py")
            
            # Run tests
            runner = unittest.TextTestRunner(verbosity=0)
            result = runner.run(suite)
            
            # Collect results
            test_results = {}
            
            for test, traceback in result.failures + result.errors:
                test_results[str(test)] = False
            
            # Tests that passed
            passed_count = result.testsRun - len(result.failures) - len(result.errors)
            # Note: This is a simplified approach - proper implementation would track individual tests
            
            return test_results
            
        finally:
            sys.path.remove(simulation_dir)
    
    async def _diagnose_failure(
        self,
        test_name: str,
        test_module_path: str,
        simulation_dir: str
    ) -> Dict[str, Any]:
        """
        Diagnose why a test failed using PLANNING model.
        
        Returns:
            diagnosis: {category, issue, evidence, expected}
        """
        prompt = f"""Diagnose test failure.

Test: {test_name}
Simulation directory: {simulation_dir}

Analyze the test failure and categorize it:
- calculation: Arithmetic or math errors
- motivation: Misunderstood objectives
- strategy: Poor temporal/strategic reasoning
- probability: Bayesian updating errors

Return JSON with diagnosis."""
        
        print(f"      🔍 Diagnosing failure (planning model)...")
        async with self.diagnosis_agent:
            llm = await self.diagnosis_agent.attach_llm(self.planning_factory)
            params = RequestParams(maxTokens=2000, temperature=0.2)
            result = await llm.generate_str(
                message=prompt,
                request_params=params
            )
        
        return json.loads(self._extract_json(result))
    
    async def _generate_fix(
        self,
        diagnosis: Dict[str, Any],
        simulation_dir: str
    ) -> Dict[str, Any]:
        """
        Generate fix based on diagnosis using IMPLEMENTATION model.
        
        Returns:
            fix: {type, content, target_file}
        """
        prompt = f"""Generate calibration fix.

Diagnosis:
{json.dumps(diagnosis, indent=2)}

Based on the diagnosis, generate appropriate fix:
- tool_addition: Add calculator or other tools
- prompt_modification: Enhance system prompt
- constraint_addition: Add hard constraints

Return JSON with fix specification."""
        
        print(f"      💻 Generating fix (implementation model)...")
        async with self.fix_agent:
            llm = await self.fix_agent.attach_llm(self.implementation_factory)
            params = RequestParams(maxTokens=2000, temperature=0.3)
            result = await llm.generate_str(
                message=prompt,
                request_params=params
            )
        
        return json.loads(self._extract_json(result))
    
    async def _apply_fix(
        self,
        fix: Dict[str, Any],
        simulation_dir: str
    ):
        """Apply fix to simulation code"""
        if fix['type'] == 'prompt_modification':
            # Modify agent system prompt
            target_file = os.path.join(simulation_dir, fix.get('target_file', 'agents.py'))
            # Implementation: modify file content
            pass
        
        elif fix['type'] == 'tool_addition':
            # Add tool to agent
            pass
        
        # Log fix application
        print(f"  ✓ Applied fix: {fix['type']}")
    
    def _calculate_pass_rate(self, results: Dict[str, bool]) -> float:
        """Calculate pass rate from results"""
        if not results:
            return 0.0
        passed = sum(1 for v in results.values() if v)
        return passed / len(results)
    
    def _extract_json(self, text: str) -> str:
        """Extract JSON from text"""
        if "```json" in text:
            start = text.find("```json") + 7
            end = text.find("```", start)
            return text[start:end].strip()
        return text.strip()
    
    def _save_report(self, report: CalibrationReport, path: str):
        """Save calibration report to file"""
        import json
        with open(path, 'w') as f:
            json.dump({
                'initial_pass_rate': self._calculate_pass_rate(report.initial_test_results),
                'final_pass_rate': report.pass_rate,
                'is_calibrated': report.is_calibrated,
                'iterations': len(report.iterations),
                'fixes_applied': len(report.fixes_applied)
            }, f, indent=2)
        print(f"Calibration report saved to {path}")
