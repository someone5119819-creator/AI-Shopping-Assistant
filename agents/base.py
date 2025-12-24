"""
Base Agent class for multi-agent system.
All specialized agents inherit from this base.
"""
import logging
from typing import Dict, List, Optional
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class Agent(ABC):
    """Base class for all agents in the system."""
    
    def __init__(self, name: str, role: str):
        """
        Initialize agent.
        
        Args:
            name: Agent identifier
            role: Agent's primary responsibility
        """
        self.name = name
        self.role = role
        logger.info(f"Initialized {name} agent with role: {role}")
    
    @abstractmethod
    def process(self, context: Dict) -> Dict:
        """
        Process a request with given context.
        
        Args:
            context: Dictionary containing conversation state, user input, etc.
            
        Returns:
            Dictionary with agent's response and updated context
        """
        pass
    
    def log_action(self, action: str, details: str = ""):
        """Log agent action for debugging."""
        logger.info(f"[{self.name}] {action} {details}")
