"""
Guardrail Agent - Safety and validation checks.
Runs BEFORE other agents to enforce restrictions.
"""
import logging
from typing import Dict, List
from agents.base import Agent

logger = logging.getLogger(__name__)


class GuardrailAgent(Agent):
    """Enforces safety rules and category restrictions."""
    
    FORBIDDEN_TOPICS = [
        "software", "code", "programming", "ide", "editor",
        "computer", "laptop", "pc", "general electronics"
    ]
    
    ALLOWED_CATEGORIES = [
        "camera", "lens", "filter", "lighting", "light",
        "audio", "microphone", "mic", "headphone", "speaker",
        "tripod", "gimbal", "stabilizer", "mount", "accessory"
    ]
    
    def __init__(self):
        super().__init__(
            name="Guardrail",
            role="Safety validation and category restriction enforcement"
        )
    
    def process(self, context: Dict) -> Dict:
        """
        Validate request against safety rules.
        
        Args:
            context: Contains 'user_message' and other state
            
        Returns:
            Dictionary with 'approved' boolean and optional 'rejection_message'
        """
        user_message = context.get('user_message', '').lower()
        
        # Check forbidden topics
        for topic in self.FORBIDDEN_TOPICS:
            if topic in user_message:
                self.log_action("REJECTED", f"Forbidden topic: {topic}")
                return {
                    'approved': False,
                    'rejection_message': "I specialize strictly in camera and audio gear."
                }
        
        # All checks passed
        self.log_action("APPROVED", "Request passed safety checks")
        return {'approved': True}
