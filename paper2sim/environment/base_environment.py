"""
Base Game Environment

Abstract base class for game environments.
All environments must inherit from this and implement the interface.
"""

from abc import ABC, abstractmethod
from typing import Dict, Tuple, Any
from dataclasses import dataclass


@dataclass
class GameState:
    """Base class for game state"""
    pass


class BaseGameEnvironment(ABC):
    """
    Abstract base class for game environments
    
    Environment enforces:
    - State transitions (deterministic math)
    - Payoff calculations (utility functions from paper)
    - Information structure (what each player observes)
    - Hard constraints (action feasibility)
    
    CRITICAL: Environment must be pure Python - NO LLM calls.
    """
    
    def __init__(self, **params):
        """
        Initialize environment with game parameters
        
        Args:
            **params: Game-specific parameters (costs, probabilities, etc.)
        """
        self.params = params
        self.state = None
        self.history = []
        self.payoffs = {}
    
    @abstractmethod
    def reset(self) -> Dict[str, Any]:
        """
        Reset environment to initial state
        
        Returns:
            initial_observation: What players observe at start
        """
        pass
    
    @abstractmethod
    def step(
        self,
        actions: Dict[str, str]
    ) -> Tuple[Dict[str, Any], Dict[str, float], bool, Dict]:
        """
        Execute one step of the game
        
        Args:
            actions: Dictionary mapping player_name -> action_string
        
        Returns:
            observations: What each player observes (may differ!)
            rewards: Immediate payoffs this step
            done: Whether game has ended
            info: Additional information (for logging)
        """
        pass
    
    @abstractmethod
    def get_observation(self, player: str) -> Dict[str, Any]:
        """
        Get player-specific observation
        
        Enforces information structure: players only see what they should see.
        
        Args:
            player: Player name
        
        Returns:
            observation: State information visible to this player
        """
        pass
    
    @abstractmethod
    def calculate_payoff(self, player: str) -> float:
        """
        Calculate cumulative payoff for a player
        
        Args:
            player: Player name
        
        Returns:
            total_payoff: Sum of all rewards so far
        """
        pass
    
    @abstractmethod
    def is_action_legal(self, player: str, action: str) -> bool:
        """
        Check if action is legal in current state
        
        Args:
            player: Player name
            action: Proposed action
        
        Returns:
            legal: True if action is allowed
        """
        pass
    
    def get_history(self) -> list:
        """Get complete history of actions and states"""
        return self.history.copy()
    
    def get_state(self) -> GameState:
        """Get current state (for debugging/logging)"""
        return self.state
