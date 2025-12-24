"""
Investigator Agent - Needs discovery and requirement gathering.
ZERO product knowledge - only asks questions.
"""
import logging
from typing import Dict
from agents.base import Agent

logger = logging.getLogger(__name__)


class InvestigatorAgent(Agent):
    """Discovers user needs through targeted questions."""
    
    DISCOVERY_PROMPT = """You are a needs discovery specialist for camera/audio equipment.
Your ONLY job is to ask 1-2 clarifying questions to understand the user's specific needs.

CRITICAL RULES:
- NEVER mention specific product names or brands
- NEVER say "I recommend" or "I suggest"
- Ask about: use case, environment, budget, experience level
- Keep questions natural and conversational

User message: {user_message}

Ask 1-2 clarifying questions:"""
    
    def __init__(self, ollama_generator):
        super().__init__(
            name="Investigator", 
            role="Needs discovery through questions"
        )
        self.ollama_generator = ollama_generator
    
    def process(self, context: Dict) -> Dict:
        """
        Generate discovery questions based on user message.
        
        Args:
            context: Contains 'user_message' and conversation history
            
        Returns:
            Dictionary with 'response' containing questions
        """
        user_message = context.get('user_message', '')
        
        # Build prompt
        prompt = self.DISCOVERY_PROMPT.format(user_message=user_message)
        
        # Generate questions using LLM
        questions = self.ollama_generator([
            {"role": "system", "content": prompt},
            {"role": "user", "content": user_message}
        ])
        
        self.log_action("GENERATED_QUESTIONS", f"Asked about: {user_message[:50]}")
        
        return {
            'response': questions,
            'next_agent': 'investigator'  # Stay in discovery until requirements clear
        }
