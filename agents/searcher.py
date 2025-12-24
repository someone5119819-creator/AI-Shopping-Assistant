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
    
    def extract_product_type(self, requirements: str) -> str:
        """
        Extract core product type from requirements.
        Avoid overly specific queries that return accessories.
        
        Args:
            requirements: User's stated needs
            
        Returns:
            Clean product type query
        """
        requirements_lower = requirements.lower()
        
        # Priority: Extract primary product type
        # Handle 'camera' and common typos
        if any(w in requirements_lower for w in ['action camera', 'action cam']):
            return "action camera"
        elif any(w in requirements_lower for w in ['camera', 'camers', 'camer', 'camra']):
            return "camera"
        elif 'microphone' in requirements_lower or 'mic' in requirements_lower:
            return "microphone"
        elif 'lighting' in requirements_lower or 'light' in requirements_lower:
            return "lighting"
        elif 'tripod' in requirements_lower:
            return "tripod"
        elif 'gimbal' in requirements_lower or 'stabilizer' in requirements_lower:
            return "gimbal"
        else:
            # Fallback to first few words
            return ' '.join(requirements_lower.split()[:3])
    
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
            # Multi-category search - extract clean product types
            clean_categories = [self.extract_product_type(cat) for cat in categories]
            self.log_action("MULTI_SEARCH", f"{len(clean_categories)} categories")
            products = self.multi_search_function(clean_categories)
        else:
            # Single search - use clean product type
            clean_query = self.extract_product_type(requirements)
            self.log_action("SINGLE_SEARCH", clean_query)
            products = self.search_function(clean_query, limit=3)
        
        return {
            'search_results': products,
            'next_agent': 'presenter'  # Send results to Presenter
        }
