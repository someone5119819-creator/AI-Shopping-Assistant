"""
Presenter Agent - Recommendation specialist with reasoning.
ZERO knowledge outside search results.
"""
import logging
from typing import Dict, List
from agents.base import Agent

logger = logging.getLogger(__name__)


class PresenterAgent(Agent):
    """Selects and explains best products from search results."""
    
    PRESENTER_PROMPT = """You are a recommendation specialist for camera/audio equipment.

ZERO KNOWLEDGE RULE:
- You have ZERO knowledge of products outside the search results below
- You CANNOT use training data or memory
- ONLY mention products by EXACT title from search results

MANDATORY REASONING:
- For EVERY product, explain WHY it's the best choice
- Format: "The [Exact Product Name] because [specific reason]"
- Reference user's specific needs

Search Results:
{search_results}

User Requirements:
{requirements}

Select top 1-2 products and explain why:"""
    
    def __init__(self, ollama_generator):
        super().__init__(
            name="Presenter",
            role="Product recommendation with reasoning"
        )
        self.ollama_generator = ollama_generator
    
    def format_search_results(self, products: List[Dict]) -> str:
        """Format products for prompt."""
        if not products:
            return "No products found."
        
        formatted = []
        for p in products:
            title = p.get('title', 'Unknown')
            price = p.get('variants', [{}])[0].get('price', 'N/A')
            formatted.append(f"- {title} (Price: {price})")
        
        return "\n".join(formatted)
    
    def process(self, context: Dict) -> Dict:
        """
        Generate recommendations from search results.
        
        Args:
            context: Contains 'search_results' and 'requirements'
            
        Returns:
            Dictionary with 'response' and 'products'
        """
        products = context.get('search_results', [])
        requirements = context.get('requirements', context.get('user_message', ''))
        
        if not products:
            self.log_action("NO_RESULTS", "Empty search results")
            return {
                'response': "I don't have any products matching that description in stock.",
                'products': []
            }
        
        # Format results for prompt
        results_text = self.format_search_results(products)
        
        # Build prompt
        prompt = self.PRESENTER_PROMPT.format(
            search_results=results_text,
            requirements=requirements
        )
        
        # Generate recommendation
        recommendation = self.ollama_generator([
            {"role": "system", "content": prompt},
            {"role": "user", "content": requirements}
        ])
        
        self.log_action("PRESENTED", f"{len(products)} products")
        
        return {
            'response': recommendation,
            'products': products[:2]  # Max 2 products
        }
