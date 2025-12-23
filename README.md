# Shopify RAG Knowledge Base

A production-ready RAG (Retrieval Augmented Generation) system for semantic search on Shopify products. This system fetches products from your Shopify store, generates embeddings, stores them in a vector database, and provides powerful semantic search capabilities through both Python API and REST API.

## 🌟 Features

- **Semantic Search**: Find products using natural language queries
- **Vector Database**: ChromaDB for efficient similarity search
- **Local Embeddings**: Free Sentence Transformers (no API keys needed)
- **REST API**: FastAPI-based HTTP endpoints for easy integration
- **Advanced Filtering**: Search by price range, category, vendor, and more
- **Similar Products**: Find products similar to a reference item
- **RAG Integration**: Optional LLM integration for natural language responses
- **Production Ready**: Proper error handling, rate limiting, and configuration management

## 📋 Prerequisites

- Python 3.8 or higher
- Shopify store with Admin API access
- Shopify Admin API access token

## 🚀 Quick Start

### 1. Installation

```bash
# Clone or navigate to the project directory
cd shopify_rag

# Create a virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration

Create a `.env` file from the template:

```bash
cp .env.example .env
```

Edit `.env` and add your Shopify credentials:

```env
SHOPIFY_SHOP_URL=https://your-store.myshopify.com
SHOPIFY_API_VERSION=2025-10
SHOPIFY_ACCESS_TOKEN=your_access_token_here
```

### 3. Fetch and Index Products

```bash
# Fetch products from Shopify
python shopify_fetcher.py

# Process and index products (this will take a few minutes on first run)
python -c "
from vector_store import VectorStore
from data_processor import ProductDataProcessor
import json

with open('products.json', 'r') as f:
    products = json.load(f)

processor = ProductDataProcessor()
documents = processor.process_products(products)

store = VectorStore()
store.add_documents(documents)
"
```

### 4. Try It Out!

```bash
# Run basic search examples
python examples/basic_search.py

# Run RAG query examples
python examples/rag_query.py

# Or start the REST API
python api.py
# Then visit http://localhost:8000/docs for interactive API documentation
```

## 💡 Usage Examples

### Python API

```python
from search import ProductSearch

# Initialize search
search = ProductSearch()

# Basic search
results = search.search("comfortable running shoes", top_k=5)

# Search with price range
results = search.search_by_price_range(
    query="headphones",
    min_price=20.0,
    max_price=100.0,
    top_k=5
)

# Find similar products
similar = search.get_similar_products(product_id="12345", top_k=5)

# Print results
for result in results:
    print(f"{result['metadata']['title']} - ${result['metadata']['price']}")
    print(f"Relevance: {result['relevance_score']:.2%}\n")
```

### REST API

Start the server:
```bash
python api.py
```

Make requests:
```bash
# Search products
curl "http://localhost:8000/search?q=wireless+headphones&top_k=5"

# Search with filters
curl "http://localhost:8000/search?q=shoes&vendor=Nike&top_k=5"

# Get statistics
curl "http://localhost:8000/stats"

# Re-index products
curl -X POST "http://localhost:8000/index" \
  -H "Content-Type: application/json" \
  -d '{"force_refresh": true}'
```

### Full RAG with LLM

For natural language responses, set your OpenAI API key:

```bash
export OPENAI_API_KEY=your_key_here
```

Then use the RAG query engine:

```python
from examples.rag_query import RAGQueryEngine

rag = RAGQueryEngine()
response = rag.query("I need a gift for my tech-savvy friend")
print(response)
```

## 📁 Project Structure

```
shopify_rag/
├── config.py              # Configuration management
├── shopify_fetcher.py     # Fetch products from Shopify
├── data_processor.py      # Process products into searchable documents
├── embeddings.py          # Generate embeddings using Sentence Transformers
├── vector_store.py        # ChromaDB vector database operations
├── search.py              # High-level search interface
├── api.py                 # FastAPI REST API
├── requirements.txt       # Python dependencies
├── .env.example          # Environment variables template
├── .gitignore            # Git ignore file
└── examples/
    ├── basic_search.py    # Basic search examples
    └── rag_query.py       # Full RAG with LLM examples
```

## 🔍 Search Capabilities

### 1. Semantic Search
Find products using natural language:
- "comfortable walking shoes" → Finds shoes with comfort-related features
- "waterproof backpack" → Finds bags with water resistance
- "gift for tech lover" → Finds technology products

### 2. Filtered Search
Combine semantic search with metadata filters:
- Search by vendor
- Search by product type
- Search by availability

### 3. Price Range Search
Find products within a specific price range while maintaining semantic relevance.

### 4. Similar Products
Given a product, find similar items based on semantic similarity.

## 🛠️ API Endpoints

### `GET /`
API information and available endpoints

### `GET /health`
Health check and database statistics

### `GET|POST /search`
Search for products
- **Parameters**: `q` (query), `top_k`, `min_score`, `vendor`, `product_type`

### `GET /stats`
Vector database statistics

### `POST /index`
Re-index products from Shopify
- **Body**: `{"force_refresh": true}` to fetch fresh data

## ⚙️ Configuration Options

Edit `.env` to customize:

| Variable | Description | Default |
|----------|-------------|---------|
| `SHOPIFY_SHOP_URL` | Your Shopify store URL | Required |
| `SHOPIFY_ACCESS_TOKEN` | Admin API access token | Required |
| `SHOPIFY_API_VERSION` | Shopify API version | 2025-10 |
| `EMBEDDING_MODEL` | Sentence transformer model | all-MiniLM-L6-v2 |
| `CHROMA_PERSIST_DIRECTORY` | Vector DB storage path | ./chroma_db |
| `COLLECTION_NAME` | ChromaDB collection name | shopify_products |
| `API_HOST` | API server host | 0.0.0.0 |
| `API_PORT` | API server port | 8000 |
| `OPENAI_API_KEY` | OpenAI API key (optional) | - |

## 🧪 Testing

Run the example scripts to verify everything works:

```bash
# Basic search examples
python examples/basic_search.py

# RAG query examples (works with or without OpenAI)
python examples/rag_query.py

# Test API
python api.py  # In one terminal
curl "http://localhost:8000/search?q=test"  # In another
```

## 📊 Performance

- **Embedding Model**: `all-MiniLM-L6-v2` (384 dimensions)
- **Indexing Speed**: ~100-200 products/second
- **Search Speed**: <100ms for typical queries
- **Storage**: ~1KB per product (embeddings + metadata)

## 🔐 Security Notes

- Never commit `.env` file to version control
- Keep your Shopify access token secure
- Use environment variables in production
- Consider rate limiting for the API in production

## 🚀 Deployment

For production deployment:

1. **Set environment variables** instead of using `.env` file
2. **Use a process manager** like `supervisor` or `systemd`
3. **Add authentication** to API endpoints
4. **Enable CORS properly** in `api.py`
5. **Use a reverse proxy** like Nginx
6. **Monitor vector DB size** and set up backups

Example systemd service:

```ini
[Unit]
Description=Shopify RAG API
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/path/to/shopify_rag
Environment="SHOPIFY_ACCESS_TOKEN=xxx"
ExecStart=/path/to/venv/bin/python api.py
Restart=always

[Install]
WantedBy=multi-user.target
```

## 🤝 Contributing

Feel free to submit issues and enhancement requests!

## 📄 License

This project is provided as-is for educational and commercial use.

## 🙋 Support

For issues or questions:
1. Check the examples in `examples/`
2. Review API documentation at `http://localhost:8000/docs`
3. Verify your `.env` configuration

## 🎯 Future Enhancements

- [ ] Hybrid search (semantic + keyword)
- [ ] Multi-language support
- [ ] Product image search
- [ ] Analytics and search insights
- [ ] Caching layer for common queries
- [ ] Batch indexing optimization
- [ ] Web UI for search

---

**Built with:** Python, Sentence Transformers, ChromaDB, FastAPI
