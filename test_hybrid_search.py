"""
Test script to compare semantic vs hybrid search results.
"""
from search import ProductSearch
import json


def test_search_comparison():
    """Compare semantic and hybrid search results."""
    
    print("="*80)
    print("SEARCH COMPARISON: Semantic vs Hybrid")
    print("="*80)
    
    # Test queries
    test_queries = [
        "LED ring light",
        "wireless bluetooth headphones",
        "camera tripod stand",
        "professional photography equipment",
        "portable projector"
    ]
    
    for query in test_queries:
        print(f"\n{'='*80}")
        print(f"Query: '{query}'")
        print(f"{'='*80}\n")
        
        # Semantic search only
        print("🔍 SEMANTIC SEARCH ONLY:")
        print("-" * 80)
        semantic_search = ProductSearch(use_hybrid=False)
        semantic_results = semantic_search.search(query, top_k=5)
        
        for i, result in enumerate(semantic_results[:3], 1):
            title = result['metadata']['title'][:65]
            price = result['metadata'].get('price', 'N/A')
            score = result.get('relevance_score', 0)
            print(f"{i}. {title}...")
            print(f"   Score: {score:.3f} | Price: ${price}")
        
        # Hybrid search
        print(f"\n🎯 HYBRID SEARCH (Semantic + Keyword):")
        print("-" * 80)
        hybrid_search = ProductSearch(use_hybrid=True, semantic_weight=0.5, keyword_weight=0.5)
        hybrid_results = hybrid_search.search(query, top_k=5)
        
        for i, result in enumerate(hybrid_results[:3], 1):
            title = result['metadata']['title'][:65]
            price = result['metadata'].get('price', 'N/A')
            hybrid_score = result.get('hybrid_score', 0)
            sem_score = result.get('semantic_score', 0)
            kw_score = result.get('keyword_score', 0)
            
            print(f"{i}. {title}...")
            print(f"   Hybrid: {hybrid_score:.3f} | Semantic: {sem_score:.3f} | Keyword: {kw_score:.3f}")
            print(f"   Price: ${price}")
        
        print()


def test_field_weighting():
    """Test field weighting in keyword search."""
    
    print("\n" + "="*80)
    print("FIELD WEIGHTING TEST")
    print("="*80)
    
    search = ProductSearch(use_hybrid=True)
    
    # Query that should match multiple fields
    query = "LED light"
    
    print(f"\nQuery: '{query}'")
    print("Showing field score breakdown for top results:\n")
    
    results = search.search(query, top_k=5)
    
    for i, result in enumerate(results, 1):
        if 'hybrid_score' in result:
            print(f"{i}. {result['metadata']['title'][:60]}...")
            print(f"   Hybrid Score: {result['hybrid_score']:.3f}")
            print(f"   Semantic: {result.get('semantic_score', 0):.3f} | "
                  f"Keyword: {result.get('keyword_score', 0):.3f}")
            
            # Show field scores if available
            field_scores = result.get('field_scores', {})
            if field_scores:
                print(f"   Field scores:")
                for field, score in sorted(field_scores.items(), key=lambda x: x[1], reverse=True):
                    if score > 0:
                        print(f"     - {field}: {score:.3f}")
            print()


def test_weight_tuning():
    """Test different semantic/keyword weight combinations."""
    
    print("\n" + "="*80)
    print("WEIGHT TUNING TEST")
    print("="*80)
    
    query = "camera for photography"
    
    weight_configs = [
        (0.7, 0.3, "Semantic-focused"),
        (0.5, 0.5, "Balanced"),
        (0.3, 0.7, "Keyword-focused")
    ]
    
    print(f"\nQuery: '{query}'\n")
    
    for sem_w, kw_w, label in weight_configs:
        print(f"{'='*80}")
        print(f"{label} (Semantic: {sem_w}, Keyword: {kw_w})")
        print(f"{'='*80}")
        
        search = ProductSearch(use_hybrid=True, semantic_weight=sem_w, keyword_weight=kw_w)
        results = search.search(query, top_k=3)
        
        for i, result in enumerate(results, 1):
            title = result['metadata']['title'][:60]
            hybrid = result.get('hybrid_score', 0)
            print(f"{i}. {title}...")
            print(f"   Score: {hybrid:.3f}")
        print()


def main():
    """Run all tests."""
    test_search_comparison()
    test_field_weighting()
    test_weight_tuning()
    
    print("\n" + "="*80)
    print("✅ All tests completed!")
    print("="*80)


if __name__ == "__main__":
    main()
