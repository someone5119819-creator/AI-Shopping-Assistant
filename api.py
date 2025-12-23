"""
FastAPI REST API for semantic product search.
Provides HTTP endpoints for searching Shopify products.
"""
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import uvicorn

from search import ProductSearch
from vector_store import VectorStore
from shopify_fetcher import ShopifyFetcher
from data_processor import ProductDataProcessor
from config import config


# Pydantic models
class SearchRequest(BaseModel):
    """Search request model."""
    query: str = Field(..., description="Search query text")
    top_k: int = Field(5, ge=1, le=50, description="Number of results")
    min_score: float = Field(0.0, ge=0.0, le=1.0, description="Minimum relevance score")
    filters: Optional[Dict[str, str]] = Field(None, description="Metadata filters")
    use_hybrid: Optional[bool] = Field(True, description="Use hybrid search (semantic + keyword)")
    semantic_weight: Optional[float] = Field(0.5, ge=0.0, le=1.0, description="Weight for semantic score")
    keyword_weight: Optional[float] = Field(0.5, ge=0.0, le=1.0, description="Weight for keyword score")


class SearchResponse(BaseModel):
    """Search response model."""
    query: str
    results: List[Dict[str, Any]]
    count: int


class IndexRequest(BaseModel):
    """Index request model."""
    force_refresh: bool = Field(False, description="Force refresh from Shopify API")


class StatsResponse(BaseModel):
    """Stats response model."""
    collection_name: str
    total_documents: int
    persist_directory: str


# Initialize FastAPI app
app = FastAPI(
    title="Shopify Product Search API",
    description="Semantic search API for Shopify products using RAG",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize search
search = ProductSearch()


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Shopify Product Search API",
        "version": "1.0.0",
        "endpoints": {
            "search": "/search",
            "stats": "/stats",
            "index": "/index",
            "health": "/health"
        }
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    try:
        stats = search.vector_store.get_stats()
        return {
            "status": "healthy",
            "documents": stats["total_documents"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unhealthy: {str(e)}")


@app.post("/search", response_model=SearchResponse)
async def search_products(request: SearchRequest):
    """
    Search for products using semantic or hybrid search.
    
    Args:
        request: Search request with query and parameters
        
    Returns:
        Search results
    """
    try:
        results = search.search(
            query=request.query,
            top_k=request.top_k,
            min_score=request.min_score,
            filters=request.filters,
            use_hybrid=request.use_hybrid,
            semantic_weight=request.semantic_weight,
            keyword_weight=request.keyword_weight
        )
        
        return SearchResponse(
            query=request.query,
            results=results,
            count=len(results)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/search")
async def search_products_get(
    q: str = Query(..., description="Search query"),
    top_k: int = Query(5, ge=1, le=50, description="Number of results"),
    min_score: float = Query(0.0, ge=0.0, le=1.0, description="Minimum score"),
    vendor: Optional[str] = Query(None, description="Filter by vendor"),
    product_type: Optional[str] = Query(None, description="Filter by product type"),
    use_hybrid: bool = Query(True, description="Use hybrid search"),
    semantic_weight: float = Query(0.5, ge=0.0, le=1.0, description="Semantic weight"),
    keyword_weight: float = Query(0.5, ge=0.0, le=1.0, description="Keyword weight")
):
    """
    Search for products using GET method (for easy browser testing).
    
    Args:
        q: Search query
        top_k: Number of results
        min_score: Minimum relevance score
        vendor: Vendor filter
        product_type: Product type filter
        
    Returns:
        Search results
    """
    filters = {}
    if vendor:
        filters["vendor"] = vendor
    if product_type:
        filters["product_type"] = product_type
    
    try:
        results = search.search(
            query=q,
            top_k=top_k,
            min_score=min_score,
            filters=filters or None,
            use_hybrid=use_hybrid,
            semantic_weight=semantic_weight,
            keyword_weight=keyword_weight
        )
        
        return {
            "query": q,
            "results": results,
            "count": len(results)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/stats", response_model=StatsResponse)
async def get_stats():
    """
    Get vector store statistics.
    
    Returns:
        Statistics about the vector database
    """
    try:
        stats = search.vector_store.get_stats()
        return StatsResponse(**stats)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/index")
async def index_products(request: IndexRequest):
    """
    Index or re-index products from Shopify.
    
    Args:
        request: Index request with options
        
    Returns:
        Indexing status
    """
    try:
        # Fetch products
        fetcher = ShopifyFetcher()
        
        if request.force_refresh:
            print("Fetching fresh products from Shopify...")
            products = fetcher.get_all_products()
            fetcher.save_products(products)
        else:
            # Try to load from file first
            products = fetcher.load_products()
            if not products:
                print("No cached products, fetching from Shopify...")
                products = fetcher.get_all_products()
                fetcher.save_products(products)
        
        # Process products
        processor = ProductDataProcessor()
        documents = processor.process_products(products)
        
        # Reset and index
        search.vector_store.reset_collection()
        search.vector_store.add_documents(documents)
        
        return {
            "status": "success",
            "products_fetched": len(products),
            "documents_indexed": len(documents),
            "message": "Products indexed successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def main():
    """Run the API server."""
    print(f"Starting API server on {config.API_HOST}:{config.API_PORT}")
    uvicorn.run(
        app,
        host=config.API_HOST,
        port=config.API_PORT,
        log_level="info"
    )


if __name__ == "__main__":
    main()
