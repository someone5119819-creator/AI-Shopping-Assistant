"""
Full RAG query example with LLM integration.
Demonstrates using OpenAI to generate natural language responses based on retrieved products.
"""
import os
from typing import List, Dict, Any
from search import ProductSearch

# Optional: Only import if OpenAI key is available
try:
    from langchain_openai import ChatOpenAI
    from langchain.prompts import ChatPromptTemplate
    from langchain.schema import SystemMessage, HumanMessage
    OPENAI_AVAILABLE = bool(os.getenv("OPENAI_API_KEY"))
except ImportError:
    OPENAI_AVAILABLE = False
    print("Warning: langchain-openai not installed or OpenAI key not set")


class RAGQueryEngine:
    """RAG query engine with LLM integration."""
    
    def __init__(self):
        """Initialize the RAG query engine."""
        self.search = ProductSearch()
        
        if OPENAI_AVAILABLE:
            self.llm = ChatOpenAI(
                model="gpt-3.5-turbo",
                temperature=0.7
            )
        else:
            self.llm = None
    
    def format_products_for_context(self, results: List[Dict[str, Any]]) -> str:
        """
        Format search results into context for LLM.
        
        Args:
            results: Search results
            
        Returns:
            Formatted context string
        """
        if not results:
            return "No products found."
        
        context_parts = []
        for i, result in enumerate(results, 1):
            meta = result['metadata']
            product_info = f"""
Product {i}:
- Title: {meta.get('title', 'N/A')}
- Price: ${meta.get('price', 'N/A')}
- Type: {meta.get('product_type', 'N/A')}
- Vendor: {meta.get('vendor', 'N/A')}
- Description: {result.get('text', 'N/A')[:300]}...
- Availability: {'In Stock' if meta.get('available') else 'Out of Stock'}
- Relevance Score: {result.get('relevance_score', 0):.2f}
"""
            context_parts.append(product_info.strip())
        
        return "\n\n".join(context_parts)
    
    def query_without_llm(self, query: str, top_k: int = 5) -> str:
        """
        Perform RAG query without LLM (fallback).
        
        Args:
            query: User query
            top_k: Number of products to retrieve
            
        Returns:
            Formatted response
        """
        results = self.search.search(query, top_k=top_k)
        
        if not results:
            return f"I couldn't find any products matching '{query}'."
        
        response_parts = [
            f"I found {len(results)} products related to '{query}':\n"
        ]
        
        for i, result in enumerate(results, 1):
            meta = result['metadata']
            response_parts.append(
                f"\n{i}. **{meta.get('title', 'N/A')}**"
                f"\n   - Price: ${meta.get('price', 'N/A')}"
                f"\n   - Type: {meta.get('product_type', 'N/A')}"
                f"\n   - Vendor: {meta.get('vendor', 'N/A')}"
                f"\n   - Match Score: {result.get('relevance_score', 0):.2%}"
            )
        
        return "\n".join(response_parts)
    
    def query_with_llm(self, query: str, top_k: int = 5) -> str:
        """
        Perform RAG query with LLM.
        
        Args:
            query: User query
            top_k: Number of products to retrieve
            
        Returns:
            Natural language response from LLM
        """
        if not self.llm:
            return self.query_without_llm(query, top_k)
        
        # Retrieve relevant products
        results = self.search.search(query, top_k=top_k)
        
        if not results:
            return f"I couldn't find any products matching '{query}' in our catalog."
        
        # Format context
        context = self.format_products_for_context(results)
        
        # Create prompt
        system_message = """You are a helpful shopping assistant for an e-commerce store. 
Your job is to help customers find products by providing personalized recommendations 
based on the product catalog.

When responding:
1. Be friendly and conversational
2. Highlight the most relevant products
3. Mention key features like price, availability, and unique selling points
4. If asked for recommendations, explain why certain products match their needs
5. Keep responses concise but informative

Base your responses ONLY on the provided product information."""

        human_message = f"""Customer Query: {query}

Available Products:
{context}

Please provide a helpful response to the customer based on these products."""

        # Get LLM response
        messages = [
            SystemMessage(content=system_message),
            HumanMessage(content=human_message)
        ]
        
        response = self.llm.invoke(messages)
        return response.content
    
    def query(self, query: str, top_k: int = 5, use_llm: bool = None) -> str:
        """
        Perform RAG query.
        
        Args:
            query: User query
            top_k: Number of products to retrieve
            use_llm: Whether to use LLM (auto-detect if None)
            
        Returns:
            Response string
        """
        if use_llm is None:
            use_llm = OPENAI_AVAILABLE and self.llm is not None
        
        if use_llm:
            return self.query_with_llm(query, top_k)
        else:
            return self.query_without_llm(query, top_k)


def main():
    """Run RAG query examples."""
    print("\n" + "="*70)
    print("FULL RAG QUERY EXAMPLES")
    print("="*70 + "\n")
    
    rag = RAGQueryEngine()
    
    # Example queries
    queries = [
        "I need a gift for my tech-savvy friend",
        "What are your most affordable products?",
        "Show me premium quality items",
        "I'm looking for something practical for everyday use",
        "What's good for outdoor activities?"
    ]
    
    for query in queries:
        print(f"\n{'='*70}")
        print(f"Q: {query}")
        print(f"{'='*70}\n")
        
        response = rag.query(query, top_k=3)
        print(response)
        print()
    
    print("\n" + "="*70)
    print("✅ RAG query examples completed!")
    print("="*70 + "\n")
    
    if not OPENAI_AVAILABLE:
        print("\n💡 TIP: Set OPENAI_API_KEY environment variable to enable LLM responses")
        print("   Without it, you'll get simple formatted results instead of natural language.\n")


if __name__ == "__main__":
    main()
