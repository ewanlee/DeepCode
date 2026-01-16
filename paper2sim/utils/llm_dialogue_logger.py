#!/usr/bin/env python3
"""
LLM Dialogue Logger for Paper2Sim
=================================

Records complete LLM inputs (prompts) and outputs (responses) to files.
Each test session gets a unique timestamped directory to prevent overwriting.
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional


class LLMDialogueLogger:
    """
    Logger for recording complete LLM dialogue (prompts and responses).
    
    Creates a unique timestamped directory for each session and saves:
    - Full prompts sent to LLM
    - Raw responses from LLM
    - Parsed/processed results
    - Session metadata
    """
    
    def __init__(self, base_output_dir: str = "./test_phase1_output", session_name: str = None):
        """
        Initialize the LLM dialogue logger.
        
        Args:
            base_output_dir: Base directory for all test outputs
            session_name: Optional custom session name (default: timestamp)
        """
        # Create unique session directory with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.session_name = session_name or f"session_{timestamp}"
        self.session_dir = Path(base_output_dir) / self.session_name
        
        # Create subdirectories
        self.logs_dir = self.session_dir / "llm_logs"
        self.results_dir = self.session_dir / "results"
        
        self.session_dir.mkdir(parents=True, exist_ok=True)
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        self.results_dir.mkdir(parents=True, exist_ok=True)
        
        # Track call counts for each agent
        self.call_counts: Dict[str, int] = {}
        
        # Session metadata
        self.session_metadata = {
            "session_name": self.session_name,
            "start_time": datetime.now().isoformat(),
            "base_output_dir": str(base_output_dir),
            "logs": []
        }
        
        print(f"📁 LLM Dialogue Logger initialized")
        print(f"   Session directory: {self.session_dir}")
        print(f"   LLM logs: {self.logs_dir}")
        print(f"   Results: {self.results_dir}")
    
    def log_llm_call(
        self,
        agent_name: str,
        phase: str,
        prompt: str,
        response: str,
        model: str = "",
        request_params: Dict[str, Any] = None,
        extra_context: Dict[str, Any] = None
    ) -> str:
        """
        Log a complete LLM call (prompt + response).
        
        Args:
            agent_name: Name of the agent making the call (e.g., "TheTheorist")
            phase: Phase of the call (e.g., "game_model_extraction", "analysis", "coding")
            prompt: Complete prompt sent to LLM
            response: Raw response from LLM
            model: Model name used
            request_params: Request parameters (temperature, max_tokens, etc.)
            extra_context: Additional context information
            
        Returns:
            Path to the log directory for this call
        """
        # Increment call count for this agent
        self.call_counts[agent_name] = self.call_counts.get(agent_name, 0) + 1
        call_num = self.call_counts[agent_name]
        
        # Create call-specific directory
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]  # Include milliseconds
        call_dir_name = f"{call_num:03d}_{agent_name}_{phase}_{timestamp}"
        call_dir = self.logs_dir / call_dir_name
        call_dir.mkdir(parents=True, exist_ok=True)
        
        # Save prompt
        prompt_file = call_dir / "prompt.txt"
        with open(prompt_file, 'w', encoding='utf-8') as f:
            f.write(prompt)
        
        # Save raw response
        response_file = call_dir / "response.txt"
        with open(response_file, 'w', encoding='utf-8') as f:
            f.write(response)
        
        # Save metadata
        metadata = {
            "agent_name": agent_name,
            "phase": phase,
            "call_number": call_num,
            "timestamp": datetime.now().isoformat(),
            "model": model,
            "request_params": request_params or {},
            "extra_context": extra_context or {},
            "prompt_length": len(prompt),
            "response_length": len(response),
            "files": {
                "prompt": "prompt.txt",
                "response": "response.txt"
            }
        }
        
        metadata_file = call_dir / "metadata.json"
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        
        # Update session metadata
        self.session_metadata["logs"].append({
            "call_dir": call_dir_name,
            "agent_name": agent_name,
            "phase": phase,
            "timestamp": metadata["timestamp"],
            "model": model,
            "prompt_length": len(prompt),
            "response_length": len(response)
        })
        
        # Save updated session metadata
        self._save_session_metadata()
        
        print(f"   📝 Logged LLM call: {call_dir_name}")
        print(f"      Prompt: {len(prompt):,} chars | Response: {len(response):,} chars")
        
        return str(call_dir)
    
    def log_system_prompt(
        self,
        agent_name: str,
        system_prompt: str
    ):
        """
        Log the system prompt for an agent.
        
        Args:
            agent_name: Name of the agent
            system_prompt: The system prompt/instruction
        """
        system_prompts_dir = self.logs_dir / "system_prompts"
        system_prompts_dir.mkdir(parents=True, exist_ok=True)
        
        prompt_file = system_prompts_dir / f"{agent_name}_system_prompt.txt"
        with open(prompt_file, 'w', encoding='utf-8') as f:
            f.write(system_prompt)
        
        print(f"   📋 Logged system prompt for {agent_name}")
    
    def save_result(
        self,
        result_name: str,
        result_data: Any,
        result_format: str = "json"
    ) -> str:
        """
        Save a processed result.
        
        Args:
            result_name: Name for the result file (without extension)
            result_data: The data to save
            result_format: Format to save in ("json", "txt", "py")
            
        Returns:
            Path to the saved result file
        """
        if result_format == "json":
            result_file = self.results_dir / f"{result_name}.json"
            with open(result_file, 'w', encoding='utf-8') as f:
                json.dump(result_data, f, indent=2, ensure_ascii=False)
        elif result_format == "py":
            result_file = self.results_dir / f"{result_name}.py"
            with open(result_file, 'w', encoding='utf-8') as f:
                f.write(result_data)
        else:
            result_file = self.results_dir / f"{result_name}.txt"
            with open(result_file, 'w', encoding='utf-8') as f:
                f.write(str(result_data))
        
        print(f"   💾 Saved result: {result_file}")
        return str(result_file)
    
    def _save_session_metadata(self):
        """Save the session metadata file."""
        metadata_file = self.session_dir / "session_metadata.json"
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(self.session_metadata, f, indent=2, ensure_ascii=False)
    
    def finalize(self, summary: Dict[str, Any] = None):
        """
        Finalize the logging session.
        
        Args:
            summary: Optional summary information to add
        """
        self.session_metadata["end_time"] = datetime.now().isoformat()
        self.session_metadata["total_llm_calls"] = sum(self.call_counts.values())
        self.session_metadata["calls_per_agent"] = self.call_counts.copy()
        
        if summary:
            self.session_metadata["summary"] = summary
        
        self._save_session_metadata()
        
        print(f"\n✅ LLM Dialogue Logger finalized")
        print(f"   Total LLM calls: {self.session_metadata['total_llm_calls']}")
        print(f"   Session directory: {self.session_dir}")
    
    def get_session_dir(self) -> Path:
        """Get the session directory path."""
        return self.session_dir
    
    def get_results_dir(self) -> Path:
        """Get the results directory path."""
        return self.results_dir


# Global shared logger instance
_shared_logger: Optional[LLMDialogueLogger] = None


def get_shared_logger() -> Optional[LLMDialogueLogger]:
    """Get the shared logger instance."""
    return _shared_logger


def set_shared_logger(logger: LLMDialogueLogger):
    """Set the shared logger instance."""
    global _shared_logger
    _shared_logger = logger


# Example usage
if __name__ == "__main__":
    # Test the logger
    logger = LLMDialogueLogger(base_output_dir="./test_output")
    
    # Log a sample LLM call
    logger.log_llm_call(
        agent_name="TestAgent",
        phase="test_phase",
        prompt="This is a test prompt for the LLM.",
        response="This is the LLM's response to the test prompt.",
        model="test-model",
        request_params={"temperature": 0.2, "max_tokens": 1000}
    )
    
    # Save a sample result
    logger.save_result("test_result", {"key": "value"}, "json")
    
    # Finalize
    logger.finalize({"status": "test completed"})
    
    print("\n✅ LLM Dialogue Logger test completed")
