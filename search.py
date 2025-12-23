"""
Semantic search functionality for Shopify products.
High-level interface for searching products with hybrid search support.
"""
from typing import List, Dict, Any, Optional
from vector_store import VectorStore
from hybrid_search import HybridSearchEngine
from data_processor import ProductDataProcessor
import json
import os


class ProductSearch:
    """High-level product search interface with hybrid search."""
    
    def __init__(self, use_hybrid: bool = True, semantic_weight: float = 0.5, keyword_weight: float = 0.5):
        """
        Initialize the search interface.
        
        Args:
            use_hybrid: Use hybrid search (semantic + keyword)
            semantic_weight: Weight for semantic scores
            keyword_weight: Weight for keyword scores
        """
        self.vector_store = VectorStore()
        self.use_hybrid = use_hybrid
        self.hybrid_engine = None
        
        # Initialize hybrid search if enabled
        if use_hybrid:
            # Load documents for keyword search
            if os.path.exists("products.json"):
                with open("products.json", "r", encoding="utf-8") as f:
                    products = json.load(f)
                processor = ProductDataProcessor()
                documents = processor.process_products(products)
                
                self.hybrid_engine = HybridSearchEngine(
                    vector_store=self.vector_store,
                    documents=documents,
                    semantic_weight=semantic_weight,
                    keyword_weight=keyword_weight
                )
            else:
                print("Warning: products.json not found, hybrid search disabled")
                self.use_hybrid = False
    
    def search(
        self,
        query: str,
        top_k: int = 5,
        min_score: float = 0.0,
        filters: Optional[Dict] = None,
        use_hybrid: Optional[bool] = None,
        semantic_weight: Optional[float] = None,
        keyword_weight: Optional[float] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for products using semantic or hybrid search.
        
        Args:
            query: Search query text
            top_k: Number of results to return
            min_score: Minimum relevance score (0-1)
            filters: Metadata filters (e.g., {"vendor": "Nike", "product_type": "Shoes"})
            use_hybrid: Override to enable/disable hybrid search for this query
            semantic_weight: Weight for semantic scores (0-1)
            keyword_weight: Weight for keyword scores (0-1)
            
        Returns:
            List of matching products with metadata
        """
        # Determine search mode
        should_use_hybrid = use_hybrid if use_hybrid is not None else self.use_hybrid
        
        # Use hybrid search if available and enabled
        if should_use_hybrid and self.hybrid_engine:
            results = self.hybrid_engine.search(
                query=query,
                top_k=top_k,
                semantic_weight=semantic_weight,
                keyword_weight=keyword_weight,
                min_score=min_score
            )
            return results
        
        # Fall back to pure semantic search
        results = self.vector_store.search(
            query=query,
            n_results=top_k,
            where_filter=filters
        )
        
        # Filter by minimum score
        filtered_results = [
            r for r in results["results"]
            if r["relevance_score"] >= min_score
        ]
        
        return filtered_results
    
    def search_by_price_range(
        self,
        query: str,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Search products within a price range.
        
        Args:
            query: Search query text
            min_price: Minimum price
            max_price: Maximum price
            top_k: Number of results to return
            
        Returns:
            List of matching products
        """
        results = self.search(query, top_k=top_k * 2)  # Get more to filter
        
        # Filter by price
        filtered = []
        for r in results:
            price = r["metadata"].get("price")
            if price is None:
                continue
            
            if min_price is not None and price < min_price:
                continue
            if max_price is not None and price > max_price:
                continue
            
            filtered.append(r)
            if len(filtered) >= top_k:
                break
        
        return filtered
    
    def search_by_category(
        self,
        query: str,
        product_type: Optional[str] = None,
        vendor: Optional[str] = None,
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Search products by category/type.
        
        Args:
            query: Search query text
            product_type: Product type filter
            vendor: Vendor filter
            top_k: Number of results to return
            
        Returns:
            List of matching products
        """
        filters = {}
        if product_type:
            filters["product_type"] = product_type
        if vendor:
            filters["vendor"] = vendor
        
        return self.search(query, top_k=top_k, filters=filters or None)
    
    def get_similar_products(
        self,
        product_id: str,
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Find similar products to a given product.
        
        Args:
            product_id: ID of the reference product
            top_k: Number of similar products to return
            
        Returns:
            List of similar products
        """
        # Get the product document
        collection = self.vector_store.collection
        result = collection.get(ids=[product_id])
        
        if not result["documents"]:
            return []
        
        # Use the product text as query
        product_text = result["documents"][0]
        results = self.search(product_text, top_k=top_k + 1)
        
        # Remove the original product from results
        return [r for r in results if r["product_id"] != product_id][:top_k]
    
    def format_result(self, result: Dict[str, Any]) -> str:
        """
        Format a search result for display.
        
        Args:
            result: Search result dictionary
            
        Returns:
            Formatted string
        """
        meta = result["metadata"]
        lines = [
            f"Title: {meta.get('title', 'N/A')}",
            f"Score: {result.get('relevance_score', 0):.3f}",
            f"Price: ${meta.get('price', 'N/A')}",
            f"Type: {meta.get('product_type', 'N/A')}",
            f"Vendor: {meta.get('vendor', 'N/A')}",
            f"Available: {'Yes' if meta.get('available') else 'No'}",
        ]
        
        if meta.get("tags"):
            lines.append(f"Tags: {meta['tags'][:100]}")
        
        return "\n".join(lines)


def main():
    """Test the search functionality."""
    search = ProductSearch()
    
    # Test queries
    queries = [
        "comfortable running shoes",
        "leather wallet",
        "wireless headphones",
        "organic cotton shirt"
    ]
    
    print("=== Semantic Product Search Demo ===\n")
    
    for query in queries:
        print(f"\n🔍 Query: '{query}'")
        print("-" * 60)
        
        results = search.search(query, top_k=3)
        
        if not results:
            print("No results found")
            continue
        
        for i, result in enumerate(results, 1):
            print(f"\n{i}. {search.format_result(result)}")


if __name__ == "__main__":
    main()
