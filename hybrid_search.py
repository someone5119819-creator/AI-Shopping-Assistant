"""
Hybrid search combining semantic and keyword-based search.
Provides advanced ranking with configurable weights.
"""
from typing import List, Dict, Any, Optional
import numpy as np
from keyword_search import KeywordSearchEngine
from vector_store import VectorStore


class HybridSearchEngine:
    """
    Hybrid search combining semantic (vector) and keyword (BM25) search.
    """
    
    def __init__(
        self,
        vector_store: VectorStore,
        documents: List[Dict[str, Any]],
        semantic_weight: float = 0.5,
        keyword_weight: float = 0.5,
        field_weights: Optional[Dict[str, float]] = None
    ):
        """
        Initialize hybrid search engine.
        
        Args:
            vector_store: Vector store for semantic search
            documents: List of documents (same order as in vector store)
            semantic_weight: Weight for semantic scores (0-1)
            keyword_weight: Weight for keyword scores (0-1)
            field_weights: Custom weights for fields in keyword search
        """
        self.vector_store = vector_store
        self.documents = documents
        self.semantic_weight = semantic_weight
        self.keyword_weight = keyword_weight
        
        # Initialize keyword search
        self.keyword_engine = KeywordSearchEngine(documents, field_weights)
        
        # Validate weights
        total = semantic_weight + keyword_weight
        if abs(total - 1.0) > 0.01:
            print(f"Warning: Weights sum to {total}, normalizing to 1.0")
            self.semantic_weight = semantic_weight / total
            self.keyword_weight = keyword_weight / total
    
    def _normalize_scores(self, scores: List[float]) -> List[float]:
        """
        Normalize scores to 0-1 range using min-max normalization.
        
        Args:
            scores: List of scores
            
        Returns:
            Normalized scores
        """
        if not scores or len(scores) == 0:
            return scores
        
        scores_array = np.array(scores)
        min_score = scores_array.min()
        max_score = scores_array.max()
        
        if max_score == min_score:
            return [0.5] * len(scores)
        
        normalized = (scores_array - min_score) / (max_score - min_score)
        return normalized.tolist()
    
    def search(
        self,
        query: str,
        top_k: int = 10,
        semantic_weight: Optional[float] = None,
        keyword_weight: Optional[float] = None,
        boost_exact_match: bool = True,
        min_score: float = 0.0
    ) -> List[Dict[str, Any]]:
        """
        Perform hybrid search combining semantic and keyword search.
        
        Args:
            query: Search query
            top_k: Number of results to return
            semantic_weight: Override default semantic weight
            keyword_weight: Override default keyword weight
            boost_exact_match: Apply boost for exact title matches
            min_score: Minimum final score threshold
            
        Returns:
            Ranked list of results with scores
        """
        # Use provided weights or defaults
        sem_w = semantic_weight if semantic_weight is not None else self.semantic_weight
        kw_w = keyword_weight if keyword_weight is not None else self.keyword_weight
        
        # Normalize weights
        total = sem_w + kw_w
        sem_w = sem_w / total
        kw_w = kw_w / total
        
        # 1. Perform semantic search (get more results for better ranking)
        search_k = min(top_k * 3, 100)
        semantic_results = self.vector_store.search(query, n_results=search_k)
        
        # 2. Perform keyword search
        keyword_results = self.keyword_engine.search(query, top_k=search_k)
        
        # 3. Create lookup maps
        semantic_scores = {}
        for result in semantic_results.get("results", []):
            product_id = result["product_id"]
            semantic_scores[product_id] = result["relevance_score"]
        
        keyword_scores_map = {}
        for result in keyword_results:
            product_id = result["document"]["metadata"]["product_id"]
            keyword_scores_map[product_id] = {
                "score": result["keyword_score"],
                "field_scores": result["field_scores"]
            }
        
        # 4. Get all unique product IDs
        all_product_ids = set(semantic_scores.keys()) | set(keyword_scores_map.keys())
        
        # 5. Normalize scores
        sem_score_list = [semantic_scores.get(pid, 0.0) for pid in all_product_ids]
        kw_score_list = [keyword_scores_map.get(pid, {}).get("score", 0.0) for pid in all_product_ids]
        
        sem_normalized = self._normalize_scores(sem_score_list)
        kw_normalized = self._normalize_scores(kw_score_list)
        
        # 6. Combine scores
        combined_results = []
        for i, product_id in enumerate(all_product_ids):
            sem_score = sem_normalized[i]
            kw_score = kw_normalized[i]
            
            # Weighted combination
            final_score = (sem_w * sem_score) + (kw_w * kw_score)
            
            # Apply boosts
            if boost_exact_match:
                # Get product title
                for result in semantic_results.get("results", []):
                    if result["product_id"] == product_id:
                        title = result["metadata"].get("title", "").lower()
                        query_lower = query.lower()
                        
                        # Exact match boost
                        if query_lower in title:
                            final_score += 0.3
                        
                        # Title starts with query boost
                        if title.startswith(query_lower):
                            final_score += 0.2
                        
                        break
            
            # Find the full result object
            full_result = None
            for result in semantic_results.get("results", []):
                if result["product_id"] == product_id:
                    full_result = result
                    break
            
            if full_result and final_score >= min_score:
                combined_results.append({
                    **full_result,
                    "hybrid_score": final_score,
                    "semantic_score": sem_score,
                    "keyword_score": kw_score,
                    "semantic_weight": sem_w,
                    "keyword_weight": kw_w,
                    "field_scores": keyword_scores_map.get(product_id, {}).get("field_scores", {})
                })
        
        # 7. Sort by hybrid score
        combined_results.sort(key=lambda x: x["hybrid_score"], reverse=True)
        
        return combined_results[:top_k]
    
    def explain_score(self, result: Dict[str, Any]) -> str:
        """
        Generate explanation for a search result score.
        
        Args:
            result: Search result dictionary
            
        Returns:
            Human-readable explanation
        """
        lines = [
            f"Product: {result['metadata']['title']}",
            f"Final Score: {result.get('hybrid_score', 0):.3f}",
            "",
            "Score Breakdown:",
            f"  Semantic: {result.get('semantic_score', 0):.3f} (weight: {result.get('semantic_weight', 0):.2f})",
            f"  Keyword:  {result.get('keyword_score', 0):.3f} (weight: {result.get('keyword_weight', 0):.2f})",
        ]
        
        field_scores = result.get('field_scores', {})
        if field_scores:
            lines.append("\n  Field Scores:")
            for field, score in sorted(field_scores.items(), key=lambda x: x[1], reverse=True):
                if score > 0:
                    lines.append(f"    {field}: {score:.3f}")
        
        return "\n".join(lines)


def main():
    """Test hybrid search."""
    from data_processor import ProductDataProcessor
    import json
    
    # Load products
    with open("products.json", "r", encoding="utf-8") as f:
        products = json.load(f)
    
    # Process documents
    processor = ProductDataProcessor()
    documents = processor.process_products(products)
    
    # Initialize stores
    vector_store = VectorStore()
    hybrid_engine = HybridSearchEngine(
        vector_store=vector_store,
        documents=documents,
        semantic_weight=0.5,
        keyword_weight=0.5
    )
    
    # Test search
    print("=== Hybrid Search Test ===\n")
    
    queries = [
        "LED ring light",
        "wireless headphones",
        "camera tripod"
    ]
    
    for query in queries:
        print(f"\n🔍 Query: '{query}'")
        print("-" * 70)
        
        results = hybrid_engine.search(query, top_k=3)
        
        for i, result in enumerate(results, 1):
            print(f"\n{i}. {result['metadata']['title'][:60]}...")
            print(f"   Hybrid: {result['hybrid_score']:.3f} | "
                  f"Semantic: {result['semantic_score']:.3f} | "
                  f"Keyword: {result['keyword_score']:.3f}")


if __name__ == "__main__":
    main()
