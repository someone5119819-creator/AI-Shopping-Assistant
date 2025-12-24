"""
Searcher Agent - Database query specialist.
NO recommendation logic - only executes searches.
"""
import logging
from typing import Dict, List
from agents.base import Agent

logger = logging.getLogger(__name__)


class SearcherAgent(Agent):
    """Executes database searches and returns structured results."""
    
    def __init__(self, search_function, multi_search_function):
        super().__init__(
            name="Searcher",
            role="Database query execution"
        )
        self.search_function = search_function
        self.multi_search_function = multi_search_function
    
    def detect_categories(self, requirements: str) -> List[str]:
        """
        Detect if user wants multiple product categories.
        
        Args:
            requirements: User's stated needs
            
        Returns:
            List of category queries
        """
        requirements_lower = requirements.lower()
        
        categories = []
        
        # Detect camera
        if any(word in requirements_lower for word in ['camera', 'video', 'photo']):
            categories.append(f"camera {requirements}")
        
        # Detect mic/audio
        if any(word in requirements_lower for word in ['mic', 'microphone', 'audio', 'sound']):
            categories.append(f"microphone {requirements}")
        
        # Detect lighting
        if any(word in requirements_lower for word in ['light', 'lighting', 'led']):
            categories.append(f"lighting {requirements}")
        
        # Detect tripod
        if any(word in requirements_lower for word in ['tripod', 'mount', 'stabilizer', 'gimbal']):
            categories.append(f"tripod {requirements}")
        
        return categories if len(categories) > 1 else None
    
    def process(self, context: Dict) -> Dict:
        """
        Execute search based on requirements.
        
        Args:
            context: Contains 'requirements' (user needs)
            
        Returns:
            Dictionary with 'search_results' and 'next_agent'
        """
        requirements = context.get('requirements', context.get('user_message', ''))
        
        # Detect multi-category
        categories = self.detect_categories(requirements)
        
        if categories:
            # Multi-category search
            self.log_action("MULTI_SEARCH", f"{len(categories)} categories")
            products = self.multi_search_function(categories)
        else:
            # Single search
            self.log_action("SINGLE_SEARCH", requirements[:50])
            products = self.search_function(requirements, limit=3)
        
        return {
            'search_results': products,
            'next_agent': 'presenter'  # Send results to Presenter
        }
