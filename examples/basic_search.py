"""
Basic search examples demonstrating the RAG system.
"""
from search import ProductSearch
from vector_store import VectorStore
from data_processor import ProductDataProcessor
from shopify_fetcher import ShopifyFetcher
import json
import os


def setup_vector_store():
    """Set up the vector store with products."""
    print("=== Setting Up Vector Store ===\n")
    
    # Check if we need to fetch products
    if not os.path.exists("products.json"):
        print("Products not found, fetching from Shopify...")
        fetcher = ShopifyFetcher()
        products = fetcher.get_all_products()
        fetcher.save_products(products)
    else:
        print("Loading products from products.json...")
        fetcher = ShopifyFetcher()
        products = fetcher.load_products()
    
    # Process products
    print("Processing products...")
    processor = ProductDataProcessor()
    documents = processor.process_products(products)
    
    # Check if vector store is already populated
    store = VectorStore()
    if store.collection.count() == 0:
        print("Vector store is empty, indexing products...")
        store.add_documents(documents)
    else:
        print(f"Vector store already has {store.collection.count()} products")
    
    return store


def example_basic_search():
    """Example: Basic semantic search."""
    print("\n" + "="*70)
    print("EXAMPLE 1: Basic Semantic Search")
    print("="*70 + "\n")
    
    search = ProductSearch()
    
    queries = [
        "comfortable walking shoes",
        "elegant wrist watch",
        "waterproof backpack",
        "wireless earbuds"
    ]
    
    for query in queries:
        print(f"🔍 Query: '{query}'")
        print("-" * 70)
        
        results = search.search(query, top_k=3)
        
        if not results:
            print("❌ No results found\n")
            continue
        
        for i, result in enumerate(results, 1):
            print(f"\n{i}. {result['metadata']['title']}")
            print(f"   Relevance Score: {result['relevance_score']:.3f}")
            print(f"   Price: ${result['metadata'].get('price', 'N/A')}")
            print(f"   Type: {result['metadata'].get('product_type', 'N/A')}")
            print(f"   Vendor: {result['metadata'].get('vendor', 'N/A')}")
        
        print("\n")


def example_filtered_search():
    """Example: Search with metadata filters."""
    print("\n" + "="*70)
    print("EXAMPLE 2: Filtered Search")
    print("="*70 + "\n")
    
    search = ProductSearch()
    
    # Search with vendor filter
    print("🔍 Query: 'shoes' (filtered by specific vendor)")
    print("-" * 70)
    
    # Note: Replace with actual vendor name from your products
    results = search.search("shoes", top_k=5)
    
    if results:
        vendors = set(r['metadata'].get('vendor', 'N/A') for r in results)
        print(f"Available vendors: {', '.join(vendors)}\n")
        
        for i, result in enumerate(results, 1):
            print(f"{i}. {result['metadata']['title']}")
            print(f"   Vendor: {result['metadata'].get('vendor', 'N/A')}")
            print(f"   Score: {result['relevance_score']:.3f}\n")


def example_price_range_search():
    """Example: Search within price range."""
    print("\n" + "="*70)
    print("EXAMPLE 3: Price Range Search")
    print("="*70 + "\n")
    
    search = ProductSearch()
    
    query = "accessories"
    min_price = 10.0
    max_price = 50.0
    
    print(f"🔍 Query: '{query}' (${min_price} - ${max_price})")
    print("-" * 70)
    
    results = search.search_by_price_range(
        query=query,
        min_price=min_price,
        max_price=max_price,
        top_k=5
    )
    
    if not results:
        print("❌ No results found in this price range\n")
        return
    
    for i, result in enumerate(results, 1):
        print(f"\n{i}. {result['metadata']['title']}")
        print(f"   Price: ${result['metadata'].get('price', 'N/A')}")
        print(f"   Score: {result['relevance_score']:.3f}")


def example_similar_products():
    """Example: Find similar products."""
    print("\n" + "="*70)
    print("EXAMPLE 4: Similar Products")
    print("="*70 + "\n")
    
    search = ProductSearch()
    
    # First, get a product
    results = search.search("shirt", top_k=1)
    
    if not results:
        print("❌ No products found to find similar items\n")
        return
    
    reference_product = results[0]
    product_id = reference_product['product_id']
    
    print(f"Reference Product: {reference_product['metadata']['title']}")
    print(f"Finding similar products...")
    print("-" * 70)
    
    similar = search.get_similar_products(product_id, top_k=5)
    
    if not similar:
        print("❌ No similar products found\n")
        return
    
    for i, result in enumerate(similar, 1):
        print(f"\n{i}. {result['metadata']['title']}")
        print(f"   Similarity Score: {result['relevance_score']:.3f}")
        print(f"   Price: ${result['metadata'].get('price', 'N/A')}")
        print(f"   Type: {result['metadata'].get('product_type', 'N/A')}")


def example_category_search():
    """Example: Search within specific category."""
    print("\n" + "="*70)
    print("EXAMPLE 5: Category Search")
    print("="*70 + "\n")
    
    search = ProductSearch()
    
    # Get all unique product types first
    all_results = search.search("", top_k=50)  # Get many results
    product_types = set(r['metadata'].get('product_type', 'Other') for r in all_results if r['metadata'].get('product_type'))
    
    print(f"Available categories: {', '.join(list(product_types)[:10])}\n")
    
    if product_types:
        # Search in first category
        category = list(product_types)[0]
        print(f"🔍 Searching in category: '{category}'")
        print("-" * 70)
        
        results = search.search_by_category(
            query="best quality",
            product_type=category,
            top_k=3
        )
        
        for i, result in enumerate(results, 1):
            print(f"\n{i}. {result['metadata']['title']}")
            print(f"   Type: {result['metadata'].get('product_type', 'N/A')}")
            print(f"   Score: {result['relevance_score']:.3f}")


def main():
    """Run all examples."""
    print("\n" + "="*70)
    print("SHOPIFY RAG SEMANTIC SEARCH - EXAMPLES")
    print("="*70)
    
    # Set up vector store
    setup_vector_store()
    
    # Run examples
    try:
        example_basic_search()
        example_filtered_search()
        example_price_range_search()
        example_similar_products()
        example_category_search()
        
        print("\n" + "="*70)
        print("✅ All examples completed successfully!")
        print("="*70 + "\n")
        
    except Exception as e:
        print(f"\n❌ Error running examples: {e}\n")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
