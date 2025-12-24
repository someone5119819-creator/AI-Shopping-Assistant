"""
Orchestrator Agent - Coordinates multi-agent workflow.
Routes requests to appropriate specialist agents.
"""
import logging
from typing import Dict, Optional
from agents.base import Agent
from agents.guardrail import GuardrailAgent
from agents.investigator import InvestigatorAgent
from agents.searcher import SearcherAgent
from agents.presenter import PresenterAgent

logger = logging.getLogger(__name__)


class OrchestratorAgent(Agent):
    """Coordinates workflow between specialized agents."""
    
    def __init__(self, ollama_generator, search_function, multi_search_function):
        super().__init__(
            name="Orchestrator",
            role="Multi-agent workflow coordination"
        )
        
        # Initialize all specialist agents
        self.guardrail = GuardrailAgent()
        self.investigator = InvestigatorAgent(ollama_generator)
        self.searcher = SearcherAgent(search_function, multi_search_function)
        self.presenter = PresenterAgent(ollama_generator)
        
        # Conversation state
        self.conversation_stage = "initial"  # initial, discovery, search, presentation
    
    def determine_next_agent(self, context: Dict) -> str:
        """
        Determine which agent should handle the request.
        
        Args:
            context: Conversation context and user message
            
        Returns:
            Name of next agent to invoke
        """
        user_message = context.get('user_message', '').lower()
        
        # Check if requirements are clear
        needs_keywords = ['for', 'because', 'to', 'budget', 'outdoor', 'indoor']
        has_clear_needs = any(keyword in user_message for keyword in needs_keywords)
        
        # Decision logic
        if self.conversation_stage == "initial":
            if has_clear_needs or len(user_message.split()) > 10:
                # Requirements seem clear, go to search
                return "searcher"
            else:
                # Need more info, ask questions
                return "investigator"
        
        elif self.conversation_stage == "discovery":
            # User answered questions, now search
            return "searcher"
        
        else:
            # Default to investigator for broad requests
            return "investigator"
    
    def process(self, context: Dict) -> Dict:
        """
        Route request through multi-agent pipeline.
        
        Pipeline:
        1. Guardrail - Safety check
        2. Investigator OR Searcher - Based on conversation state
        3. Presenter - If search results available
        
        Args:
            context: Contains user_message and conversation state
            
        Returns:
            Final response with products (if any)
        """
        self.log_action("ROUTING", f"Stage: {self.conversation_stage}")
        
        # STEP 1: Safety check
        guardrail_result = self.guardrail.process(context)
        if not guardrail_result.get('approved'):
            return {
                'response': guardrail_result.get('rejection_message'),
                'products': []
            }
        
        # STEP 2: Determine next agent
        next_agent_name = self.determine_next_agent(context)
        
        # STEP 3: Route to appropriate agent
        if next_agent_name == "investigator":
            # Discovery phase
            investigator_result = self.investigator.process(context)
            self.conversation_stage = "discovery"
            return {
                'response': investigator_result.get('response'),
                'products': []
            }
        
        elif next_agent_name == "searcher":
            # Search phase
            searcher_result = self.searcher.process(context)
            products = searcher_result.get('search_results', [])
            
            # STEP 4: Present results
            presenter_context = {
                'search_results': products,
                'requirements': context.get('user_message'),
                'user_message': context.get('user_message')
            }
            presenter_result = self.presenter.process(presenter_context)
            
            self.conversation_stage = "presentation"
            return {
                'response': presenter_result.get('response'),
                'products': presenter_result.get('products', [])
            }
        
        else:
            # Fallback
            return {
                'response': "I'm here to help you find camera and audio equipment. What are you looking for?",
                'products': []
            }
