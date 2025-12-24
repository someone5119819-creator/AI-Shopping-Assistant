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
    
    def is_casual_conversation(self, user_message: str) -> bool:
        """Detect if this is casual conversation, not a product request."""
        casual_patterns = [
            'hello', 'hi', 'hey', 'how are you', 'whats up', "what's up",
            'good morning', 'good afternoon', 'good evening',
            'thanks', 'thank you', 'bye', 'goodbye',
            'how do you do', 'nice to meet you'
        ]
        message_lower = user_message.lower().strip()
        
        # Check if message is short greeting/casual
        if len(message_lower.split()) <= 5:
            for pattern in casual_patterns:
                if pattern in message_lower:
                    return True
        return False
    
    def is_product_request(self, user_message: str) -> bool:
        """Detect if this is a genuine product request."""
        product_keywords = [
            'camera', 'mic', 'microphone', 'lens', 'tripod', 'lighting', 'light',
            'audio', 'video', 'gimbal', 'stabilizer', 'need', 'want', 'looking for',
            'recommend', 'buy', 'purchase', 'get', 'find', 'show me'
        ]
        message_lower = user_message.lower()
        return any(keyword in message_lower for keyword in product_keywords)
    
    def determine_next_agent(self, context: Dict) -> str:
        """
        Determine which agent should handle the request.
        
        CRITICAL FLOW:
        1. Casual conversation → "casual" response
        2. Vague product request (initial) → Investigator (ask questions)
        3. After discovery → Searcher (with gathered requirements)
        4. Detailed product request → Searcher (skip discovery)
        
        Args:
            context: Conversation context and user message
            
        Returns:
            Name of next agent to invoke
        """
        user_message = context.get('user_message', '').lower()
        
        # CRITICAL: Detect casual conversation first
        if self.is_casual_conversation(user_message):
            return "casual"  # Special case - handle in orchestrator
        
        # Check if this is clearly a product request
        is_product_req = self.is_product_request(user_message)
        
        # Determine if request has DETAILED requirements
        detail_keywords = [
            'budget', 'price', 'under', 'around',  # Budget specified
            'outdoor', 'indoor', 'travel', 'studio',  # Environment specified
            'beginner', 'professional', 'advanced',  # Skill level
            'youtube', 'vlog', 'stream', 'podcast',  # Specific use case
            '4k', '1080p', 'resolution'  # Technical specs
        ]
        has_detailed_needs = any(keyword in user_message for keyword in detail_keywords)
        is_very_detailed = len(user_message.split()) > 15  # Long, descriptive request
        
        # Decision logic based on conversation stage
        if self.conversation_stage == "initial":
            if not is_product_req:
                # Not a product request
                return "casual"
            elif has_detailed_needs or is_very_detailed:
                # Detailed request with clear requirements, can search directly
                self.log_action("SKIP_DISCOVERY", "Detailed requirements provided")
                return "searcher"
            else:
                # Product request but VAGUE - need discovery
                # Example: "I need a camera" → Ask questions!
                self.log_action("NEEDS_DISCOVERY", "Vague product request")
                return "investigator"
        
        elif self.conversation_stage == "discovery":
            # User has answered discovery questions, now search
            return "searcher"
        
        else:
            # Subsequent messages - check if new product request
            return "searcher" if is_product_req else "casual"
    
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
        if next_agent_name == "casual":
            # Handle casual conversation without product search
            casual_responses = [
                "I'm doing great, thanks for asking! I'm here to help you find camera and audio equipment. What are you looking for today?",
                "Hello! I specialize in camera and audio gear. How can I help you today?",
                "Hi there! I'm your equipment specialist. Are you looking for something specific?"
            ]
            import random
            self.conversation_stage = "initial"
            return {
                'response': random.choice(casual_responses),
                'products': []
            }
        
        elif next_agent_name == "investigator":
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
