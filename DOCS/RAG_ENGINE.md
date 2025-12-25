# RAG Engine: Hybrid Search & Data Processing

## 🏗️ The RAG Pipeline
The Retrieval-Augmented Generation system ensures the AI recommendations are grounded in the actual Shopify inventory.

### 1. Data Processing (`data_processor.py`)
*   **ETL**: Converts `products.json` into specialized searchable units.
*   **Metadata Extraction**: Captures `id`, `price`, `vendor`, `image_url` for frontend rendering.
*   **Text Normalization**: Strips HTML from Shopify descriptions and combines it with Title/Tags for embedding.

### 2. Vector Store (`chroma_db`)
*   **Database**: ChromaDB.
*   **Model**: `all-MiniLM-L6-v2`.
*   **Function**: Stores 384-dimensional vectors for semantic lookup.

### 3. Hybrid Search Ranker (`hybrid_search.py`)
This is the "secret sauce" for accuracy. It fuses two distinct scoring methods:

#### **A. Semantic Score (50%)**
*   Captures intent (e.g., "landscape photography" matches products tagged "wide-angle").
*   Uses Cosine Similarity from ChromaDB.

#### **B. Keyword Score (BM25) (50%)**
*   Captures precision (e.g., "A7S III").
*   **Field Weighting**:
    *   **Title**: 3.0x (Matches here are prioritized).
    *   **Description**: 2.0x.
    *   **Tags**: 1.5x.

### 4. Search Flow
1.  **Query Input**: "Professional vlogging camera".
2.  **Semantic Retrieval**: Finds 5-10 contextually similar items.
3.  **Keyword Ranking**: Calculates BM25 for those same items.
4.  **Boost Logic**: Multiplies score if the query exactly matches the start of a title.
5.  **Selection**: The top 2 results are delivered to the AI.
