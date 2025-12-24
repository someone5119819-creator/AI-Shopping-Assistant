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
        self.conversation_stage = "initial"  # initial, discovery, recommendation_given, accessories_given
        self.last_recommended_product = None
    
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
    
    def calculate_confidence_score(self, user_message: str) -> int:
        """
        Calculate confidence score (0-100) for how well we understand user needs.
        Only skip discovery if score > 95%.
        
        Args:
            user_message: User's request
            
        Returns:
            Confidence score 0-100
        """
        score = 0
        message_lower = user_message.lower()
        
        # Base score from message length (max 20 points)
        word_count = len(user_message.split())
        if word_count >= 20:
            score += 20
        elif word_count >= 15:
            score += 15
        elif word_count >= 10:
            score += 10
        else:
            score += 5
        
        # Budget specified (+25 points)
        budget_keywords = ['budget', 'price', 'under', 'around', '$', '₹', 'dollar', 'rupee']
        if any(keyword in message_lower for keyword in budget_keywords):
            score += 25
        
        # Specific use case (+25 points)
        use_case_keywords = ['youtube', 'vlog', 'podcast', 'stream', 'wedding', 'event', 'travel', 'sport']
        if any(keyword in message_lower for keyword in use_case_keywords):
            score += 25
        
        # Environment specified (+15 points)
        environment_keywords = ['outdoor', 'indoor', 'studio', 'underwater', 'mountain', 'travel']
        if any(keyword in message_lower for keyword in environment_keywords):
            score += 15
        
        # Technical specs mentioned (+10 points)
        tech_keywords = ['4k', '1080p', 'resolution', 'fps', 'megapixel', 'zoom', 'stabilization']
        if any(keyword in message_lower for keyword in tech_keywords):
            score += 10
        
        # Skill level mentioned (+5 points)
        skill_keywords = ['beginner', 'professional', 'advanced', 'intermediate', 'expert']
        if any(keyword in message_lower for keyword in skill_keywords):
            score += 5
        
        self.log_action("CONFIDENCE_SCORE", f"{score}% for: '{user_message[:50]}'")
        return min(score, 100)  # Cap at 100
    
    def determine_next_agent(self, context: Dict) -> str:
        """
        Determine which agent should handle the request.
        
        CRITICAL FLOW:
        1. Casual conversation → "casual" response
        2. Calculate confidence score
        3. If confidence > 95% → Skip to Searcher
        4. If confidence <= 95% → Investigator (ask questions)
        5. After discovery → Searcher
        
        Args:
            context: Conversation context and user message
            
        Returns:
            Name of next agent to invoke
        """
        user_message = context.get('user_message', '').lower()
        
        # CRITICAL: Detect casual conversation first
        if self.is_casual_conversation(user_message):
            return "casual"
        
        # Check if this is clearly a product request
        is_product_req = self.is_product_request(user_message)
        
        # Decision logic based on conversation stage
        if self.conversation_stage == "initial":
            if not is_product_req:
                # Not a product request
                return "casual"
            
            # Calculate confidence score
            confidence = self.calculate_confidence_score(user_message)
            
            if confidence > 95:
                # Very high confidence - skip discovery
                self.log_action("SKIP_DISCOVERY", f"Confidence: {confidence}% (>95%)")
                return "searcher"
            else:
                # Low confidence - need discovery
                self.log_action("NEEDS_DISCOVERY", f"Confidence: {confidence}% (≤95%)")
                return "investigator"
        
        elif self.conversation_stage == "discovery":
            # User has answered discovery questions, now search
            return "searcher"

        elif self.conversation_stage == "recommendation_given":
            # If user agrees/likes it -> Cross sell
            # Simple check for now: if not negative, assume interest
            negative_keywords = ['no', 'bad', 'don\'t like', 'expensive', 'something else']
            if not any(k in user_message for k in negative_keywords):
                return "cross_sell"
            else:
                # User didn't like it, search for something else
                return "searcher"
        
        elif self.conversation_stage == "accessories_given":
             # User saw accessories -> Cart/Close
             return "casual" # For now, will implement cart logic later or just let them talk
        
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
        Main orchestration logic.
        """
        user_message = context.get('user_message', '')
        self.log_action("PROCESSING", f"Stage: {self.conversation_stage}")
        
        # 1. Determine next agent
        next_agent_name = self.determine_next_agent(context)
        self.log_action("ROUTING", f"Next agent: {next_agent_name}")
        
        # 2. Execute agent
        if next_agent_name == "casual":
            # Handle casually
            return {
                'response': self.ollama_generator([
                    {"role": "system", "content": "You are a helpful shopping assistant. Be warm and professional. If the user greets you, greet them back and ask how you can help with camera/audio gear."},
                    {"role": "user", "content": user_message}
                ])
            }
            
        elif next_agent_name == "investigator":
            self.conversation_stage = "discovery"
            return self.agents['investigator'].process(context)
            
        elif next_agent_name == "searcher":
                'response': "I'm here to help you find camera and audio equipment. What are you looking for?",
                'products': []
            }
