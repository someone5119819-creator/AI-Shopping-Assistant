#!/usr/bin/env python3
"""
Setup script to initialize the Shopify RAG system.
Guides users through configuration and initial indexing.
"""
import os
import sys
from pathlib import Path


def check_env_file():
    """Check if .env file exists and is configured."""
    if not os.path.exists(".env"):
        print("❌ .env file not found!")
        print("\n📝 Creating .env from template...")
        
        if os.path.exists(".env.example"):
            import shutil
            shutil.copy(".env.example", ".env")
            print("✅ Created .env file")
            print("\n⚠️  Please edit .env and add your Shopify credentials:")
            print("   - SHOPIFY_SHOP_URL")
            print("   - SHOPIFY_ACCESS_TOKEN")
            print("\nThen run this script again.")
            return False
        else:
            print("❌ .env.example not found!")
            return False
    
    # Check if configured
    from dotenv import load_dotenv
    load_dotenv()
    
    if not os.getenv("SHOPIFY_ACCESS_TOKEN"):
        print("⚠️  SHOPIFY_ACCESS_TOKEN not set in .env")
        print("Please edit .env and add your credentials.")
        return False
    
    print("✅ Configuration file found and loaded")
    return True


def install_dependencies():
    """Check and optionally install dependencies."""
    print("\n📦 Checking dependencies...")
    
    try:
        import requests
        import sentence_transformers
        import chromadb
        import fastapi
        import dotenv
        print("✅ All required packages are installed")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("\n💡 To install dependencies, run:")
        print("   pip install -r requirements.txt")
        return False


def fetch_products():
    """Fetch products from Shopify."""
    print("\n🛍️  Fetching products from Shopify...")
    
    try:
        from shopify_fetcher import ShopifyFetcher
        
        fetcher = ShopifyFetcher()
        products = fetcher.get_all_products()
        fetcher.save_products(products)
        
        print(f"✅ Fetched and saved {len(products)} products")
        return products
    except Exception as e:
        print(f"❌ Error fetching products: {e}")
        return None


def index_products(products):
    """Process and index products in vector store."""
    print("\n🔍 Processing and indexing products...")
    print("   (This may take a few minutes on first run...)")
    
    try:
        from data_processor import ProductDataProcessor
        from vector_store import VectorStore
        
        # Process products
        processor = ProductDataProcessor()
        documents = processor.process_products(products)
        
        # Index in vector store
        store = VectorStore()
        
        # Check if already indexed
        if store.collection.count() > 0:
            print(f"\n⚠️  Vector store already has {store.collection.count()} products")
            response = input("   Reset and re-index? (y/N): ").strip().lower()
            if response == 'y':
                store.reset_collection()
            else:
                print("   Skipping indexing")
                return True
        
        store.add_documents(documents)
        print(f"✅ Indexed {len(documents)} products")
        return True
        
    except Exception as e:
        print(f"❌ Error indexing products: {e}")
        import traceback
        traceback.print_exc()
        return False


def run_test_search():
    """Run a test search to verify everything works."""
    print("\n🧪 Running test search...")
    
    try:
        from search import ProductSearch
        
        search = ProductSearch()
        results = search.search("shoes", top_k=3)
        
        if results:
            print("✅ Search is working!")
            print(f"\n   Found {len(results)} results for 'shoes':")
            for i, r in enumerate(results[:3], 1):
                print(f"   {i}. {r['metadata']['title']}")
        else:
            print("⚠️  No results found, but search is functional")
        
        return True
        
    except Exception as e:
        print(f"❌ Error running test search: {e}")
        return False


def main():
    """Main setup function."""
    print("="*70)
    print("  SHOPIFY RAG KNOWLEDGE BASE - SETUP")
    print("="*70)
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher required")
        sys.exit(1)
    
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor}")
    
    # Step 1: Check environment
    if not check_env_file():
        sys.exit(1)
    
    # Step 2: Check dependencies
    if not install_dependencies():
        sys.exit(1)
    
    # Step 3: Fetch products
    products = None
    if os.path.exists("products.json"):
        print("\n📄 Found existing products.json")
        response = input("   Fetch fresh products from Shopify? (y/N): ").strip().lower()
        if response == 'y':
            products = fetch_products()
        else:
            from shopify_fetcher import ShopifyFetcher
            fetcher = ShopifyFetcher()
            products = fetcher.load_products()
    else:
        products = fetch_products()
    
    if not products:
        print("❌ Failed to load products")
        sys.exit(1)
    
    # Step 4: Index products
    if not index_products(products):
        sys.exit(1)
    
    # Step 5: Test search
    if not run_test_search():
        print("\n⚠️  Search test failed, but setup may still be functional")
    
    # Success!
    print("\n" + "="*70)
    print("  ✅ SETUP COMPLETE!")
    print("="*70)
    print("\n📚 Next steps:")
    print("   1. Run examples: python examples/basic_search.py")
    print("   2. Try RAG queries: python examples/rag_query.py")
    print("   3. Start API: python api.py")
    print("   4. View docs: http://localhost:8000/docs")
    print("\n💡 See README.md for more information\n")


if __name__ == "__main__":
    main()
